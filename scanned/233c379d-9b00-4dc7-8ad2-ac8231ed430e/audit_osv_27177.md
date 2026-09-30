# [C] Io.quarkus:quarkus-security-webauthn: quarkus webauthn unexpected authentication bypass

## Summary
Severity: Critical
Advisory: CVE-2024-12225
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-05-06
Source: https://osv.dev/vulnerability/CVE-2024-12225
Type: osv

## Details
A vulnerability was found in Quarkus in the quarkus-security-webauthn module. The Quarkus WebAuthn module publishes default REST endpoints for registering and logging users in while allowing developers to provide custom REST endpoints. When developers provide custom REST endpoints, the default endpoints remain accessible, potentially allowing attackers to obtain a login cookie that has no corresponding user in the Quarkus application or, depending on how the application is written, could correspond to an existing user that has no relation with the current attacker, allowing anyone to log in as an existing user by just knowing that user's user name.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2024-12225
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12225.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12225
- https://bugzilla.redhat.com/show_bug.cgi?id=2330484
- https://github.com/quarkusio/quarkus
