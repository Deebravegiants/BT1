# [H] CVE-2024-39719

## Summary
Severity: High
Advisory: CVE-2024-39719
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-31
Source: https://osv.dev/vulnerability/CVE-2024-39719
Type: osv

## Details
An issue was discovered in Ollama through 0.3.14. File existence disclosure can occur via api/create. When calling the CreateModel route with a path parameter that does not exist, it reflects the "File does not exist" error message to the attacker, providing a primitive for file existence on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39719.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39719
- https://www.oligo.security/blog/more-models-more-probllms
