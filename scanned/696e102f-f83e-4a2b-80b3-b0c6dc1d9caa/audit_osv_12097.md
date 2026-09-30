# [C] CVE-2018-10199

## Summary
Severity: Critical
Advisory: CVE-2018-10199
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-18
Source: https://osv.dev/vulnerability/CVE-2018-10199
Type: osv

## Details
In versions of mruby up to and including 1.4.0, a use-after-free vulnerability exists in src/io.c::File#initilialize_copy(). An attacker that can cause Ruby code to be run can possibly use this to execute arbitrary code.

## References
- https://github.com/mruby/mruby/issues/4001
- https://github.com/mruby/mruby/commit/b51b21fc63c9805862322551387d9036f2b63433
