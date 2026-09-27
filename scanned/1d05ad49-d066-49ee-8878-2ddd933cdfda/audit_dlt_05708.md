# [?] setconfig: fix crash on dynamic multi-value plugin options

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-05-11
Source: https://github.com/ElementsProject/lightning/commit/e9fee876d735135e0b939db8271418dc01a27ba7
Type: security-commit

## Details
setconfig: fix crash on dynamic multi-value plugin options

We had an assert(!(ot->type & OPT_MULTI)) which crashed when using
setconfig on a plugin option marked as both dynamic and multi.

The fix changes plugin_set_dynamic_opt to accept an array of values
(scalar options pass a 1-element array, multi options pass the complete
set). For multi options, setconfig replaces ALL values atomically - an
empty array clears them.

Fixes: #8295

Changelog-Fixed: setconfig no longer crashes on dynamic multi-value plugin options
