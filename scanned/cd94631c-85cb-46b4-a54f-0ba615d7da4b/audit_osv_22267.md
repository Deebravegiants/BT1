# [H] Stack buffer overflow in pjproject

## Summary
Severity: High
Advisory: CVE-2022-24764
Aliases: GHSA-f5qg-pqcg-765m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-22
Source: https://osv.dev/vulnerability/CVE-2022-24764
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. Versions 2.12 and prior contain a stack buffer overflow vulnerability that affects PJSUA2 users or users that call the API `pjmedia_sdp_print(), pjmedia_sdp_media_print()`. Applications that do not use PJSUA2 and do not directly call `pjmedia_sdp_print()` or `pjmedia_sdp_media_print()` should not be affected. A patch is available on the `master` branch of the `pjsip/pjproject` GitHub repository. There are currently no known workarounds.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24764.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-f5qg-pqcg-765m
- https://nvd.nist.gov/vuln/detail/CVE-2022-24764
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/560a1346f87aabe126509bb24930106dea292b00
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
