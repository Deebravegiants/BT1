# [M] Race Condition Vulnerability in mintplex-labs/anything-llm

## Summary
Severity: Medium
Advisory: CVE-2024-2913
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-2913
Type: osv

## Details
A race condition vulnerability exists in the mintplex-labs/anything-llm repository, specifically within the user invite acceptance process. Attackers can exploit this vulnerability by sending multiple concurrent requests to accept a single user invite, allowing the creation of multiple user accounts from a single invite link intended for only one user. This bypasses the intended security mechanism that restricts invite acceptance to a single user, leading to unauthorized user creation without detection in the invite tab. The issue is due to the lack of validation for concurrent requests in the backend.

## References
- https://huntr.com/bounties/a3c69faf-cca0-4c10-8739-57e5bef7a95f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2913.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2913
