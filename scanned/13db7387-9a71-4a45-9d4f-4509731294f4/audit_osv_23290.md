# [C] CVE-2022-46945

## Summary
Severity: Critical
Advisory: CVE-2022-46945
CVSS: 9.1 (CVSS:3.1/AC:L/AV:N/A:L/C:H/I:L/PR:L/S:C/UI:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2022-46945
Type: osv

## Details
Nagvis before 1.9.34 was discovered to contain an arbitrary file read vulnerability via the component /core/classes/NagVisHoverUrl.php.

## References
- https://github.com/NagVis/nagvis/compare/nagvis-1.9.33...nagvis-1.9.34
- https://lists.debian.org/debian-lts-announce/2025/05/msg00000.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46945.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46945
- https://github.com/NagVis/nagvis/commit/71aba7f46f79d846e1df037f165d206a2cd1d22a
- https://www.sonarsource.com/blog/checkmk-rce-chain-3/
