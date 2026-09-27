# [H] CVE-2014-1845

## Summary
Severity: High
Advisory: CVE-2014-1845
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-27
Source: https://osv.dev/vulnerability/CVE-2014-1845
Type: osv

## Details
An unspecified setuid root helper in Enlightenment before 0.17.6 allows local users to gain privileges by leveraging failure to properly sanitize the environment.

## References
- https://exchange.xforce.ibmcloud.com/vulnerabilities/91216
- http://www.openwall.com/lists/oss-security/2014/02/03/19
- https://git.enlightenment.org/core/enlightenment.git/commit/?id=666df815cd86a50343859bce36c5cf968c5f38b0
- https://git.enlightenment.org/core/enlightenment.git/commit/?id=bb4a21e98656fe2c7d98ba2163e6defe9a630e2b
- https://bugzilla.redhat.com/show_bug.cgi?id=1059410
