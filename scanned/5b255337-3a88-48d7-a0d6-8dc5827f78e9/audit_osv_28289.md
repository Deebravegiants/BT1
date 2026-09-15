# [M] JSON Injection in mintplex-labs/anything-llm

## Summary
Severity: Medium
Advisory: CVE-2024-3102
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-3102
Type: osv

## Details
A JSON Injection vulnerability exists in the `mintplex-labs/anything-llm` application, specifically within the username parameter during the login process at the `/api/request-token` endpoint. The vulnerability arises from improper handling of values, allowing attackers to perform brute force attacks without prior knowledge of the username. Once the password is known, attackers can conduct blind attacks to ascertain the full username, significantly compromising system security.

## References
- https://huntr.com/bounties/8af4650d-5955-44a4-86b4-d08e1c862b49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3102.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3102
- https://github.com/mintplex-labs/anything-llm/commit/2374939ffb551ab2929d7f9d5827fe6597fa8caa
