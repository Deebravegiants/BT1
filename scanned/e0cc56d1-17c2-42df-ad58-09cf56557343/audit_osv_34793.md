# [C] Deserialization of Untrusted Data in h2oai/h2o-3

## Summary
Severity: Critical
Advisory: CVE-2025-6507
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-01
Source: https://osv.dev/vulnerability/CVE-2025-6507
Type: osv

## Details
A vulnerability in the h2oai/h2o-3 repository allows attackers to exploit deserialization of untrusted data, potentially leading to arbitrary code execution and reading of system files. This issue affects the latest master branch version 3.47.0.99999. The vulnerability arises from the ability to bypass regular expression filters intended to prevent malicious parameter injection in JDBC connections. Attackers can manipulate spaces between parameters to evade detection, allowing for unauthorized file access and code execution. The vulnerability is addressed in version 3.46.0.8.

## References
- https://huntr.com/bounties/0a9d527a-2d39-4bc0-bf01-1e717587f077
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6507.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6507
- https://github.com/h2oai/h2o-3/commit/f714edd6b8429c7a7211b779b6ec108a95b7382d
