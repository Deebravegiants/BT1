# [H] sysstat Incorrect Buffer Size calculation on 32-bit systems results in RCE via buffer overflow

## Summary
Severity: High
Advisory: CVE-2022-39377
Aliases: GHSA-q8r6-g56f-9w7x
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-08
Source: https://osv.dev/vulnerability/CVE-2022-39377
Type: osv

## Details
sysstat is a set of system performance tools for the Linux operating system. On 32 bit systems, in versions 9.1.16 and newer but prior to 12.7.1, allocate_structures contains a size_t overflow in sa_common.c. The allocate_structures function insufficiently checks bounds before arithmetic multiplication, allowing for an overflow in the size allocated for the buffer representing system activities. This issue may lead to Remote Code Execution (RCE). This issue has been patched in version 12.7.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39377.json
- https://github.com/sysstat/sysstat/security/advisories/GHSA-q8r6-g56f-9w7x
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6F26ALXWYHT4LN2AHPZM34OQEXTJE3JZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7X6WKTODOUDV6M3HZMASYNZP6EM4N7W4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PHUVUDIVDJZ7AVXD3XX3NBXXXKPOKN3N/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39377
- https://security.gentoo.org/glsa/202211-07
- https://lists.debian.org/debian-lts-announce/2022/11/msg00014.html
