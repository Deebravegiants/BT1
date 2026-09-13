# [M] CVE-2023-23589

## Summary
Severity: Medium
Advisory: CVE-2023-23589
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-01-14
Source: https://osv.dev/vulnerability/CVE-2023-23589
Type: osv

## Details
The SafeSocks option in Tor before 0.4.7.13 has a logic error in which the unsafe SOCKS4 protocol can be used but not the safe SOCKS4a protocol, aka TROVE-2022-002.

## References
- https://gitlab.torproject.org/tpo/core/tor/-/raw/release-0.4.7/ReleaseNotes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23589.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IYOLTP6HQO2HPXUYKOR7P5YYYN7CINQQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZMY4FWXYKP3MDXTZ3EJ7XJVGBCKBK2XL/
- https://nvd.nist.gov/vuln/detail/CVE-2023-23589
- https://security.gentoo.org/glsa/202305-11
- https://www.debian.org/security/2023/dsa-5320
- https://gitlab.torproject.org/tpo/core/tor/-/issues/40730
- https://gitlab.torproject.org/tpo/core/tor/-/commit/a282145b3634547ab84ccd959d0537c021ff7ffc
- https://lists.debian.org/debian-lts-announce/2023/01/msg00026.html
