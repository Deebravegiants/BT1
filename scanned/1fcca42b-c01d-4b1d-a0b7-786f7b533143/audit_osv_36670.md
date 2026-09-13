# [C] Authenticated Remote Code Execution via Arbitrary File Upload

## Summary
Severity: Critical
Advisory: CVE-2026-24897
Aliases: GHSA-336w-hgpq-6369
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24897
Type: osv

## Details
Erugo is a self-hosted file-sharing platform. In versions up to and including 0.2.14, an authenticated low-privileged user can upload arbitrary files to any specified location due to insufficient validation of user‑supplied paths when creating shares.
By specifying a writable path within the public web root, an attacker can upload and execute arbitrary code on the server, resulting in remote code execution (RCE). This vulnerability allows a low-privileged user to fully compromise the affected Erugo instance. Version 0.2.15 fixes the issue.

## References
- https://github.com/ErugoOSS/Erugo/releases/tag/v0.2.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24897.json
- https://github.com/ErugoOSS/Erugo/security/advisories/GHSA-336w-hgpq-6369
- https://nvd.nist.gov/vuln/detail/CVE-2026-24897
- https://github.com/ErugoOSS/Erugo/commit/256bc63831a0b5e9a94cb024a0724e0cd5fa5e38
