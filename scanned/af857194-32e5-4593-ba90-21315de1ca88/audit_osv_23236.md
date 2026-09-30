# [C] CVE-2022-45908

## Summary
Severity: Critical
Advisory: CVE-2022-45908
Aliases: GHSA-83g7-8fch-p37m, PYSEC-2026-443
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-26
Source: https://osv.dev/vulnerability/CVE-2022-45908
Type: osv

## Details
In PaddlePaddle before 2.4, paddle.audio.functional.get_window is vulnerable to code injection because it calls eval on a user-supplied winstr. This may lead to arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45908.json
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2022-002.md
- https://nvd.nist.gov/vuln/detail/CVE-2022-45908
- https://github.com/PaddlePaddle/Paddle/commit/26c419ca386aeae3c461faf2b828d00b48e908eb
