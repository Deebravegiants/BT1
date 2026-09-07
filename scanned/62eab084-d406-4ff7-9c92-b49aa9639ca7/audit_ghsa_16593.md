# [M] OpenCMS Cross-Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vg6x-pchq-98mg
CVE: CVE-2024-5520
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-vg6x-pchq-98mg
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=16.0 <17.0

## Details
Two Cross-Site Scripting vulnerabilities have been discovered in Alkacon's OpenCMS affecting version 16, which could allow a user:
 with sufficient privileges to create and modify web pages through the admin panel, can execute malicious JavaScript code, after inserting code in the `title` field. Another could having the roles of gallery editor or VFS resource manager will have the permission to upload images in the .svg format containing JavaScript code. The code will be executed the moment another user accesses the image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5520
- https://github.com/alkacon/opencms-core/commit/b05a5aca0f2b03042ddf2b2bb45fe2243a4084a7
- https://github.com/alkacon/opencms-core
- https://www.incibe.es/en/incibe-cert/notices/aviso/cross-site-scripting-stored-alkacon-opencms
