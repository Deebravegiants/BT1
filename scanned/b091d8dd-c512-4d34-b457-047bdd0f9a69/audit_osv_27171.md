# [H] Denial of Service in imartinez/privategpt

## Summary
Severity: High
Advisory: CVE-2024-12063
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12063
Type: osv

## Details
A Denial of Service (DoS) vulnerability exists in the file upload feature of imartinez/privategpt version v0.6.2. The vulnerability is due to improper handling of form-data with a large filename in the file upload request. An attacker can exploit this by sending a payload with an excessively large filename, causing the server to become overwhelmed and unavailable to legitimate users.

## References
- https://huntr.com/bounties/7db0091f-cb53-4cde-aad7-7ce491dfd8d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12063.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12063
