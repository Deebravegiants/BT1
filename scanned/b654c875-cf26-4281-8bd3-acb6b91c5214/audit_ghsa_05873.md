# [H] Document Merge Service vulnerable to RCE via SSTI (xlsx tempaltes)

## Summary
Severity: High
Advisory: GHSA-w47q-945m-q9pc
CVE: CVE-2026-53964
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-w47q-945m-q9pc
Type: github-advisory

## Affected
- PyPI: `document-merge-service` — affected >=0 <9.1.0

## Details
### Impact
A remote code execution (RCE) via server-side template injection (SSTI) allows for user supplied code to be executed in the server's context where it is executed as the document-merge-server user with the UID 901 thus giving an attacker considerable control over the container. The vulnerability is limited to XLSX templates, were the `xltpl` library uses a npn-sandboxed Jinja environment  for the processing of the template. 

### Patches
It has been patched in [v9.1.0](https://github.com/adfinis/document-merge-service/releases/tag/v9.1.0)

### Workarounds
Disable the upload/usage of XLSX templates.

### References
Are there any links users can visit to find out more?

https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection/jinja2-ssti

## References
- https://github.com/adfinis/document-merge-service/security/advisories/GHSA-w47q-945m-q9pc
- https://github.com/adfinis/document-merge-service
- https://github.com/adfinis/document-merge-service/releases/tag/v9.1.0
