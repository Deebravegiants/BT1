# [M] CVE-2018-8048

## Summary
Severity: Medium
Advisory: CVE-2018-8048
Aliases: GHSA-x7rv-cr6v-4vm4
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2018-8048
Type: osv

## Details
In the Loofah gem through 2.2.0 for Ruby, non-whitelisted HTML attributes may occur in sanitized output by republishing a crafted HTML fragment.

## References
- http://www.openwall.com/lists/oss-security/2018/03/19/5
- https://github.com/flavorjones/loofah/issues/144
- https://security.netapp.com/advisory/ntap-20191122-0003/
- https://www.debian.org/security/2018/dsa-4171
