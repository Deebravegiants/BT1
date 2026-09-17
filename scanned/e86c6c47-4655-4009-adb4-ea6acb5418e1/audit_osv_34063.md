# [M] uv is vulnerable to ZIP payload obfuscation through parsing differentials

## Summary
Severity: Medium
Advisory: CVE-2025-54368
Aliases: GHSA-8qf3-x8v5-2pj8, PYSEC-2026-2001
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-08-08
Source: https://osv.dev/vulnerability/CVE-2025-54368
Type: osv

## Details
uv is a Python package and project manager written in Rust. In versions 0.8.5 and earlier, remote ZIP archives were handled in a streamwise fashion, and file entries were not reconciled against the archive's central directory. An attacker could contrive a ZIP archive that would extract with legitimate contents on some package installers, and malicious contents on others due to multiple local file entries. An attacker could  also contrive a "stacked" ZIP input with multiple internal ZIPs, which would be handled differently by different package installers. The attacker could choose which installer to target in both scenarios. This issue is fixed in version 0.8.6. To work around this issue, users may choose to set UV_INSECURE_NO_ZIP_VALIDATION=1 to revert to the previous behavior.

## References
- https://astral.sh/blog/uv-security-advisory-cve-2025-54368
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54368.json
- https://github.com/astral-sh/uv/security/advisories/GHSA-8qf3-x8v5-2pj8
- https://nvd.nist.gov/vuln/detail/CVE-2025-54368
- https://github.com/astral-sh/uv/commit/7f1eaf48c193e045ca2c62c4581048765c55505f
- https://blog.pypi.org/posts/2025-08-07-wheel-archive-confusion-attacks
