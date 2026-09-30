# [C] PubNet Critical Authentication Bypass Allows Unauthenticated Package Upload and Identity Spoofing

## Summary
Severity: Critical
Advisory: CVE-2025-65112
Aliases: GHSA-pg82-fqrg-q6j5
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-65112
Type: osv

## Details
PubNet is a self-hosted Dart & Flutter package service. Prior to version 1.1.3, the /api/storage/upload endpoint in PubNet allows unauthenticated users to upload packages as any user by providing arbitrary author-id values. This enables identity spoofing, privilege escalation, and supply chain attacks. This issue has been patched in version 1.1.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65112.json
- https://github.com/ricardoboss/PubNet/security/advisories/GHSA-pg82-fqrg-q6j5
- https://nvd.nist.gov/vuln/detail/CVE-2025-65112
