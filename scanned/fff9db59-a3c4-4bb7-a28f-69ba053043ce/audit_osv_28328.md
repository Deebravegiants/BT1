# [M] Uncontrolled Resource Consumption in mintplex-labs/anything-llm

## Summary
Severity: Medium
Advisory: CVE-2024-3153
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-3153
Type: osv

## Details
mintplex-labs/anything-llm is affected by an uncontrolled resource consumption vulnerability in its upload file endpoint, leading to a denial of service (DOS) condition. Specifically, the server can be shut down by sending an invalid upload request. An attacker with the ability to upload documents can exploit this vulnerability to cause a DOS condition by manipulating the upload request.

## References
- https://huntr.com/bounties/7bb08e7b-fd99-411e-99bc-07f81f474635
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3153.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3153
- https://github.com/mintplex-labs/anything-llm/commit/b8d37d9f43af2facab4c51146a46229a58cb53d9
