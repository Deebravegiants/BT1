# [M] CVE-2017-6188

## Summary
Severity: Medium
Advisory: CVE-2017-6188
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-02-22
Source: https://osv.dev/vulnerability/CVE-2017-6188
Type: osv

## Details
Munin before 2.999.6 has a local file write vulnerability when CGI graphs are enabled. Setting multiple upper_limit GET parameters allows overwriting any file accessible to the www-data user.

## References
- http://www.securityfocus.com/bid/96399
- https://security.gentoo.org/glsa/201710-05
- https://www.debian.org/security/2017/dsa-3794
- https://bugs.debian.org/855705
- https://github.com/munin-monitoring/munin/issues/721
