# [C] Budibase PWA ZIP Upload Path Traversal Allows Reading Arbitrary Server Files Including All Environment Secrets

## Summary
Severity: Critical
Advisory: CVE-2026-30240
Aliases: GHSA-pqcr-jmfv-c9cp
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-30240
Type: osv

## Details
Budibase is a low code platform for creating internal tools, workflows, and admin panels. In 3.31.5 and earlier, a path traversal vulnerability in the PWA (Progressive Web App) ZIP processing endpoint (POST /api/pwa/process-zip) allows an authenticated user with builder privileges to read arbitrary files from the server filesystem, including /proc/1/environ which contains all environment variables — JWT secrets, database credentials, encryption keys, and API tokens. The server reads attacker-specified files via unsanitized path.join() with user-controlled input from icons.json inside the uploaded ZIP, then uploads the file contents to the object store (MinIO/S3) where they can be retrieved through signed URLs. This results in complete platform compromise as all cryptographic secrets and service credentials are exfiltrated in a single request.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-pqcr-jmfv-c9cp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30240.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30240
