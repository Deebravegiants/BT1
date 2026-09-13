# [M] CVE-2023-22898

## Summary
Severity: Medium
Advisory: CVE-2023-22898
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-10
Source: https://osv.dev/vulnerability/CVE-2023-22898
Type: osv

## Details
workers/extractor.py in Pandora (aka pandora-analysis/pandora) 1.3.0 allows a denial of service when an attacker submits a deeply nested ZIP archive (aka ZIP bomb).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22898.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22898
- https://github.com/pandora-analysis/pandora/commit/1dc06327fdc07c56eae653e497dd137ec70d8265
