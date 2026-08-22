# [?] Fix potential deadlock in Validator sites:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2021-08-06
Source: https://github.com/XRPLF/rippled/commit/b8552abcea9ab693f419219fea91d80b492ca99a
Type: security-commit

## Details
Fix potential deadlock in Validator sites:

There are two mutexes in ValidatorSite: `site_mutex_` and `state_mutex_`. Some
function end up locking both mutexes. However, depending on the call, the
mutexes could be locked in different orders, resulting in deadlocks.

If both mutexes are locked, this patch always locks the `sites_mutex_` first.
