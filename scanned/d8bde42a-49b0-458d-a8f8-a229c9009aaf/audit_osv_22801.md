# [H] Buffer overflow in pjlib scanner and pjmedia

## Summary
Severity: High
Advisory: CVE-2022-39244
Aliases: GHSA-fq45-m3f7-3mhj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-10-06
Source: https://osv.dev/vulnerability/CVE-2022-39244
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. In versions of PJSIP prior to 2.13 the PJSIP parser, PJMEDIA RTP decoder, and PJMEDIA SDP parser are affeced by a buffer overflow vulnerability. Users connecting to untrusted clients are at risk. This issue has been patched and is available as commit c4d3498 in the master branch and will be included in releases 2.13 and later. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39244.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-fq45-m3f7-3mhj
- https://nvd.nist.gov/vuln/detail/CVE-2022-39244
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2023/dsa-5358
- https://github.com/pjsip/pjproject/commit/c4d34984ec92b3d5252a7d5cddd85a1d3a8001ae
- https://lists.debian.org/debian-lts-announce/2023/02/msg00029.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
