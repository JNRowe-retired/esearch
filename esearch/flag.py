#!/usr/bin/python
#
# Copyright(c) 2010, Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# This is a slightly simplified version of flag.py copied from the
# portage public_api branch being developed.

"""Provides support functions for USE flag settings and analysis"""

from portage import settings as default_settings
from portage import portdb


def get_iuse(cpv, root=None, settings=default_settings):
    """Gets the current IUSE flags from the tree

    To be used when a gentoolkit package object is not needed
    @type: cpv: string
    @param cpv: cat/pkg-ver
    @type root: string
    @param root: tree root to use
    @param settings: optional portage config settings instance.
        defaults to portage.api.settings.default_settings
    @rtype list
    @returns [] or the list of IUSE flags
    """
    if root is None:
        root = settings["ROOT"]
    try:
        return portdb.aux_get(cpv, ["IUSE"])[0].split()
    except:
        return []


def filter_flags(use, use_expand_hidden, usemasked,
        useforced, settings=default_settings):
    """Filter function to remove hidden or otherwise not normally
    visible USE flags from a list.

    @type use: list
    @param use: the USE flag list to be filtered.
    @type use_expand_hidden: list
    @param  use_expand_hidden: list of flags hidden.
    @type usemasked: list
    @param usemasked: list of masked USE flags.
    @type useforced: list
    @param useforced: the forced USE flags.
    @param settings: optional portage config settings instance.
        defaults to portage.api.settings.default_settings
    @rtype: list
    @return the filtered USE flags.
    """
    # clean out some environment flags, since they will most probably
    # be confusing for the user
    for flag in use_expand_hidden:
        flag = flag.lower() + "_"
        for expander in use:
            if flag in expander:
                use.remove(expander)
    # clean out any arch's
    archlist = settings["PORTAGE_ARCHLIST"].split()
    for key in use[:]:
        if key in archlist:
            use.remove(key)
    # dbl check if any from usemasked  or useforced are still there
    masked = usemasked + useforced
    for flag in use[:]:
        if flag in masked:
            use.remove(flag)
    return use


def get_all_cpv_use(cpv, root=None, settings=default_settings):
    """Uses portage to determine final USE flags and settings for an emerge

    @type cpv: string
    @param cpv: eg cat/pkg-ver
    @type root: string
    @param root: tree root to use
    @param settings: optional portage config settings instance.
        defaults to portage.api.settings.default_settings
    @rtype: lists
    @return  use, use_expand_hidden, usemask, useforce
    """
    if root is None:
        root = settings["ROOT"]
    use = None
    portdb.settings.unlock()
    try:
        portdb.settings.setcpv(cpv, mydb=portdb)
        use = settings['PORTAGE_USE'].split()
        use_expand_hidden = settings["USE_EXPAND_HIDDEN"].split()
        usemask = list(portdb.settings.usemask)
        useforce =  list(portdb.settings.useforce)
    except KeyError:
        portdb.settings.reset()
        portdb.settings.lock()
        return [], [], [], []
    # reset cpv filter
    portdb.settings.reset()
    portdb.settings.lock()
    return use, use_expand_hidden, usemask, useforce


def get_flags(cpv, final_setting=False, root=None, settings=default_settings):
    """Retrieves all information needed to filter out hidden, masked, etc.
    USE flags for a given package.

    @type cpv: string
    @param cpv: eg. cat/pkg-ver
    @type final_setting: boolean
    @param final_setting: used to also determine the final
        enviroment USE flag settings and return them as well.
    @type root: string
    @param root: pass through variable needed, tree root to use
        for other function calls.
    @param settings: optional portage config settings instance.
        defaults to portage.api.settings.default_settings
    @rtype: list or list, list
    @return IUSE or IUSE, final_flags
    """
    (final_use, use_expand_hidden, usemasked, useforced) = \
        get_all_cpv_use(cpv, root, settings)
    iuse_flags = filter_flags(get_iuse(cpv), use_expand_hidden,
        usemasked, useforced, settings)
    #flags = filter_flags(use_flags, use_expand_hidden,
        #usemasked, useforced, settings)
    if final_setting:
        final_flags = filter_flags(final_use,  use_expand_hidden,
            usemasked, useforced, settings)
        return iuse_flags, final_flags
    return iuse_flags
