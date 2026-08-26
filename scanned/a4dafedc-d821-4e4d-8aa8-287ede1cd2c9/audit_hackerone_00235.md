# [M] Untrusted users able to run pending migrations in production

## Summary
Severity: Medium (CVSS 6.5)
Program: Ruby on Rails
Weakness: Uncontrolled Resource Consumption
Reporter: tenderlove
State: resolved
Disclosed: 2020-07-24T20:07:32.367Z
CVE: CVE-2020-8185
Source: https://hackerone.com/reports/899069

## Details
Untrusted users able to run pending migrations in production

There is a vulnerability in versions of Rails prior to 6.0.3.2 that allowed
an untrusted user to run any pending migrations on a Rails app running in
production.

This vulnerability has been assigned the CVE identifier CVE-2020-XXXX.

Versions Affected:  6.0.0 < rails < 6.0.3.2
Not affected:       Applications with `config.action_dispatch.show_exceptions = false` (this is not a default setting in production)
Fixed Versions:     rails >= 6.0.3.2


Releases
--------

The new release (6.0.3.2) is available in the regular locations.

Workarounds
-----------

Until such time as the patch can be applied, application developers should
disable the ActionDispatch middleware in their production environment via
a line such as this one in their config/environment/production.rb:

config.middleware.delete ActionDispatch::ActionableExceptions

Patches
-------

As mentioned, we are releasing the following patch for the 6.0 release
series:

* 0001-6.0.3.1-Only-allow-ActionableErrors-if-show_detailed_excepti.patch


Credits
-------

_Trimmed to 38 lines — full report: https://hackerone.com/reports/899069_
