# [M] FeehiCMS Has a Remote Code Execution via Unrestricted File Upload in Ad Management

## Summary
Severity: Medium
Advisory: GHSA-mcxq-54f4-mmx5
CVE: CVE-2025-65657
CWE: CWE-20, CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-mcxq-54f4-mmx5
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected >=0

## Details
FeehiCMS version 2.1.1 has a Remote Code Execution via Unrestricted File Upload in Ad Management. FeehiCMS version 2.1.1 allows authenticated remote attackers to upload files that the server later executes (or stores in an executable location) without sufficient validation, sanitization, or execution restrictions. An authenticated remote attacker can upload a crafted PHP file and cause the application or web server to execute it, resulting in remote code execution (RCE).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65657
- https://github.com/liufee/cms/issues/78
- https://github.com/kiwi865/CVEs/blob/main/CVE-2025-65657.md
- https://github.com/liufee/cms
