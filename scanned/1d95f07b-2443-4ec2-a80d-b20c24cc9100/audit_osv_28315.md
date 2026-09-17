# [H] Arbitrary File Reading in DataEase

## Summary
Severity: High
Advisory: CVE-2024-31441
Aliases: GHSA-h7hj-7wg6-p5wh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-10
Source: https://osv.dev/vulnerability/CVE-2024-31441
Type: osv

## Details
DataEase is an open source data visualization analysis tool. Due to the lack of restrictions on the connection parameters for the ClickHouse data source, it is possible to exploit certain malicious parameters to achieve arbitrary file reading. The vulnerability has been fixed in v1.18.19.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31441.json
- https://github.com/dataease/dataease/security/advisories/GHSA-h7hj-7wg6-p5wh
- https://nvd.nist.gov/vuln/detail/CVE-2024-31441
