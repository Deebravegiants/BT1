# [C] CVE-2017-2628

## Summary
Severity: Critical
Advisory: CVE-2017-2628
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2017-2628
Type: osv

## Details
curl, as shipped in Red Hat Enterprise Linux 6 before version 7.19.7-53, did not correctly backport the fix for CVE-2015-3148 because it did not reflect the fact that the HAVE_GSSAPI define was meanwhile substituted by USE_HTTP_NEGOTIATE. This issue was introduced in RHEL 6.7 and affects RHEL 6 curl only.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0847.html
- http://www.securityfocus.com/bid/97187
- https://bugzilla.redhat.com/show_bug.cgi?id=1422464
