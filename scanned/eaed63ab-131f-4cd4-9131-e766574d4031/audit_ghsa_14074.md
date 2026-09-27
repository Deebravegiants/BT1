# [H] Mage-ai missing user authentication

## Summary
Severity: High
Advisory: GHSA-c6mm-2g84-v4m7
CVE: CVE-2023-31143
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-c6mm-2g84-v4m7
Type: github-advisory

## Affected
- PyPI: `mage-ai` — affected >=0.8.34 <0.8.72

## Details
### Impact

You may be impacted if you're using Mage with user authentication enabled. The terminal could be accessed by users who are not signed in or do not have editor permissions.

### Patches

The vulnerability has been resolved in Mage version 0.8.72.

## References
- https://github.com/mage-ai/mage-ai/security/advisories/GHSA-c6mm-2g84-v4m7
- https://nvd.nist.gov/vuln/detail/CVE-2023-31143
- https://github.com/mage-ai/mage-ai/commit/f63cd00f6a3be372397d37a4c9a49bfaf50d7650
- https://github.com/mage-ai/mage-ai
- https://github.com/pypa/advisory-database/tree/main/vulns/mage-ai/PYSEC-2023-64.yaml
