# [H] CVE-2026-46419

## Summary
Severity: High
Advisory: CVE-2026-46419
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-46419
Type: osv

## Details
Yubico webauthn-server-core (aka java-webauthn-server) 2.8.0 before 2.8.2 incorrectly checks a function's return value in the second factor flow, leading to impersonation.

## References
- https://github.com/Yubico/java-webauthn-server/releases/tag/2.8.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46419.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46419
- https://www.yubico.com/support/security-advisories/ysa-2026-02/
