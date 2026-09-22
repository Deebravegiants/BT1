# [M] kkFileView: Unauthenticated SSRF via /addTask with fullfilename type-confusion bypass

## Summary
Severity: Medium
Advisory: CVE-2026-73243
Aliases: GHSA-gwwj-52hv-6g2m
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73243
Type: osv

## Details
kkFileView is a universal file online preview project based on Spring Boot. Prior to 5.0.1, the unauthenticated GET /addTask endpoint in kkFileView is omitted from TrustHostFilter and TrustDirFilter in server/src/main/java/cn/keking/config/WebConfig.java, allowing FileConvertQueueTask to fetch an attacker-selected URL after FileHandlerService#getFileAttribute uses the fullfilename parameter to force an OFFICE, COMPRESS, or CAD type. This issue is fixed in version 5.0.1.

## References
- https://github.com/kekingcn/kkFileView/releases/tag/v5.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73243.json
- https://github.com/kekingcn/kkFileView/security/advisories/GHSA-gwwj-52hv-6g2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-73243
- https://github.com/kekingcn/kkFileView/issues/765
- https://github.com/kekingcn/kkFileView/commit/32a887aa2cd70228998c617c4e7df6cfcf3fe709
- https://github.com/kekingcn/kkFileView/pull/767
