# [H] Improper Input Validation in mintplex-labs/anything-llm

## Summary
Severity: High
Advisory: CVE-2024-3028
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-3028
Type: osv

## Details
mintplex-labs/anything-llm is vulnerable to improper input validation, allowing attackers to read and delete arbitrary files on the server. By manipulating the 'logo_filename' parameter in the 'system-preferences' API endpoint, an attacker can construct requests to read sensitive files or the application's '.env' file, and even delete files by setting the 'logo_filename' to the path of the target file and invoking the 'remove-logo' API endpoint. This vulnerability is due to the lack of proper sanitization of user-supplied input.

## References
- https://huntr.com/bounties/41016b86-eabb-4161-ac81-40a1ca8e82ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3028.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3028
- https://github.com/mintplex-labs/anything-llm/commit/7de23dbb2da932fbfb39f56d981784d3702cf5ce
