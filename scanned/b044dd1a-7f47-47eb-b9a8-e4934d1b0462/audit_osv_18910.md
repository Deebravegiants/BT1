# [M] CVE-2020-4030

## Summary
Severity: Medium
Advisory: CVE-2020-4030
Aliases: GHSA-fjr5-97f5-qq98
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-4030
Type: osv

## Details
In FreeRDP before version 2.1.2, there is an out of bounds read in TrioParse. Logging might bypass string length checks due to an integer overflow. This is fixed in version 2.1.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6Y35HBHG2INICLSGCIKNAR7GCXEHQACQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XOZLH35OJWIQLM7FYDXAP2EAUBDXE76V/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- http://www.freerdp.com/2020/06/22/2_1_2-released
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-fjr5-97f5-qq98
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4481-1/
- https://github.com/FreeRDP/FreeRDP/commit/05cd9ea2290d23931f615c1b004d4b2e69074e27
