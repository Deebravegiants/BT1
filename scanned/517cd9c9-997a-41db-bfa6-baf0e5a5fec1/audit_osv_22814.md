# [M] FreeRDP may read and display out of bounds data

## Summary
Severity: Medium
Advisory: CVE-2022-39283
Aliases: GHSA-6cf9-3328-qrvh
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-12
Source: https://osv.dev/vulnerability/CVE-2022-39283
Type: osv

## Details
FreeRDP is a free remote desktop protocol library and clients. All FreeRDP based clients when using the `/video` command line switch might read uninitialized data, decode it as audio/video and display the result. FreeRDP based server implementations are not affected. This issue has been patched in version 2.8.1. If you cannot upgrade do not use the `/video` switch.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/2.8.1
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39283.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-6cf9-3328-qrvh
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HEWWYMGWIMD4RDCOGHWMZXUMBGZHC5NW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RLZCF7YHNC5BECDPEJNAZUYGNNM7NFME/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UDOTAOJBCZKREZJPT6VZ25GESI5T6RBG/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39283
- https://security.gentoo.org/glsa/202210-24
- https://lists.debian.org/debian-lts-announce/2023/11/msg00010.html
