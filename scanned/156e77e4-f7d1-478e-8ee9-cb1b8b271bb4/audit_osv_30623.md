# [H] Local File Read in stitionai/devika

## Summary
Severity: High
Advisory: CVE-2024-5334
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-5334
Type: osv

## Details
A local file read vulnerability exists in the stitionai/devika repository, affecting the latest version. The vulnerability is due to improper handling of the 'snapshot_path' parameter in the '/api/get-browser-snapshot' endpoint. An attacker can exploit this vulnerability by crafting a request with a malicious 'snapshot_path' parameter, leading to arbitrary file read from the system. This issue impacts the security of the application by allowing unauthorized access to sensitive files on the server.

## References
- https://huntr.com/bounties/7eec128b-1bf5-4922-a95c-551ad3695cf6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5334.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5334
- https://github.com/stitionai/devika/commit/6acce21fb08c3d1123ef05df6a33912bf0ee77c2
