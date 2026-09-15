# [H] FlagForgeCTF Hint Exposure via API

## Summary
Severity: High
Advisory: CVE-2025-59833
Aliases: GHSA-hm85-2j65-j8j2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-59833
Type: osv

## Details
Flag Forge is a Capture The Flag (CTF) platform. In versions from 2.1.0 to before 2.3.0, the API endpoint GET /api/problems/:id returns challenge hints in plaintext within the question object, regardless of whether the user has unlocked them via point deduction. Users can view all hints for free, undermining the business logic of the platform and reducing the integrity of the challenge system. This issue has been patched in version 2.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59833.json
- https://github.com/FlagForgeCTF/flagForge/security/advisories/GHSA-hm85-2j65-j8j2
- https://nvd.nist.gov/vuln/detail/CVE-2025-59833
