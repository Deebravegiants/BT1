# [H] CVE-2024-41881

## Summary
Severity: High
Advisory: CVE-2024-41881
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41881
Type: osv

## Details
SDoP versions prior to 1.11 fails to handle appropriately some parameters inside the input data, resulting in a stack-based buffer overflow vulnerability. When a user of the affected product is tricked to process a specially crafted XML file, arbitrary code may be executed on the user's environment.

## References
- https://jvn.jp/en/jp/JVN16420523/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41881.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41881
- https://github.com/PhilipHazel/SDoP/commit/ff83d851b4b39ff2fd37ab2ab14365649515b023
- https://github.com/PhilipHazel/SDoP
