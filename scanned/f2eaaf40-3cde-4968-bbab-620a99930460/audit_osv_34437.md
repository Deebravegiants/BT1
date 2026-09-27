# [H] FlagForgeCTF Unauthenticated Resource Modification/Deletion

## Summary
Severity: High
Advisory: CVE-2025-59932
Aliases: GHSA-v8rh-25rf-gfqw
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2025-09-27
Source: https://osv.dev/vulnerability/CVE-2025-59932
Type: osv

## Details
Flag Forge is a Capture The Flag (CTF) platform. From versions 2.0.0 to before 2.3.1, the /api/resources endpoint previously allowed POST and DELETE requests without proper authentication or authorization. This could have enabled unauthorized users to create, modify, or delete resources on the platform. The issue has been fixed in FlagForge version 2.3.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59932.json
- https://github.com/FlagForgeCTF/flagForge/security/advisories/GHSA-v8rh-25rf-gfqw
- https://nvd.nist.gov/vuln/detail/CVE-2025-59932
