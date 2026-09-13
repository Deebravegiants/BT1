# [H] Zusam vulnerable to stored XSS, allowing token theft via crafted SVG

## Summary
Severity: High
Advisory: CVE-2024-51492
Aliases: GHSA-96fx-5rqv-jfxh
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:L)
Published: 2024-11-01
Source: https://osv.dev/vulnerability/CVE-2024-51492
Type: osv

## Details
Zusam is a free and open-source way to self-host private forums. Prior to version 0.5.6, specially crafted SVG files uploaded to the service as images allow for unrestricted script execution on (raw) image load. With certain payloads, theft of the target user’s long-lived session token is possible. Note that Zusam, at the time of writing, uses a user’s static API key as a long-lived session token, and these terms can be used interchangeably on the platform. This session token/API key remains valid indefinitely, so long as the user doesn’t expressly request a new one via their Settings page. Version 0.5.6 fixes the cross-site scripting vulnerability.

## References
- https://github.com/zusam/zusam/releases/tag/0.5.6
- https://pfeister.dev/CVE-2024-51492
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51492.json
- https://github.com/zusam/zusam/security/advisories/GHSA-96fx-5rqv-jfxh
- https://nvd.nist.gov/vuln/detail/CVE-2024-51492
- https://github.com/zusam/zusam/commit/5930fdf86fa4abed01f0b345c8ec3c443656db9a
