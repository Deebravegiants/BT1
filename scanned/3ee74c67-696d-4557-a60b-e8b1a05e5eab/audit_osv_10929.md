# [H] CVE-2017-5188

## Summary
Severity: High
Advisory: CVE-2017-5188
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5188
Type: osv

## Details
The bs_worker code in open build service before 20170320 followed relative symlinks, allowing reading of files outside of the package source directory during build, allowing leakage of private information.

## References
- https://www.suse.com/de-de/security/cve/CVE-2017-5188/
- https://bugzilla.suse.com/show_bug.cgi?id=1029824
- https://github.com/openSUSE/open-build-service/commit/ba27c91351878bc297ec4baba0bd488a2f3b568d
