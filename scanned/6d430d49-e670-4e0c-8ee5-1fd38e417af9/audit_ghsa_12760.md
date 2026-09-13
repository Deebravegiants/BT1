# [H] Path traversal in binwalk

## Summary
Severity: High
Advisory: GHSA-3cm8-v4mc-gppg
CVE: CVE-2022-4510
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-3cm8-v4mc-gppg
Type: github-advisory

## Affected
- PyPI: `binwalk` — affected >=2.1.2b

## Details
A path traversal vulnerability was identified in ReFirm Labs binwalk from version 2.1.2b through 2.3.3 inclusive. By crafting a malicious PFS filesystem file, an attacker can get binwalk's PFS extractor to extract files at arbitrary locations when binwalk is run in extraction mode (-e option). Remote code execution can be achieved by building a PFS filesystem that, upon extraction, would extract a malicious binwalk module into the folder .config/binwalk/plugins. This vulnerability is associated with program files src/binwalk/plugins/unpfs.py. This issue affects binwalk from 2.1.2b through and including 2.3.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4510
- https://github.com/ReFirmLabs/binwalk/pull/617
- https://github.com/ReFirmLabs/binwalk
- https://lists.debian.org/debian-lts-announce/2025/12/msg00022.html
- https://security.gentoo.org/glsa/202309-07
