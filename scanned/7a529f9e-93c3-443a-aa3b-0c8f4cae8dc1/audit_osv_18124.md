# [H] CVE-2020-24266

## Summary
Severity: High
Advisory: CVE-2020-24266
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-19
Source: https://osv.dev/vulnerability/CVE-2020-24266
Type: osv

## Details
An issue was discovered in tcpreplay tcpprep v4.3.3. There is a heap buffer overflow vulnerability in get_l2len() that can make tcpprep crash and cause a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EA7K7VKDK2K3SY2DHQQYSCBGZLKPWXJ4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LC3UMBJFBK5HYUX7H2NGXVFI2I2EMAOF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M623ONZKOZL5Y7XQNHKXEPV76XYCPXQM/
- https://security.gentoo.org/glsa/202105-21
- https://github.com/appneta/tcpreplay/issues/617
