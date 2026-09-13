# [H] WebAuthn User Verification Bypass via Session Serialization

## Summary
Severity: High
Advisory: CVE-2026-47841
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47841
Type: osv

## Details
An application using Spring Security's WebAuthn support may be vulnerable to user verification bypass when using a distributed HTTP session store.
Spring Security 7.1.0
Spring Security 7.0.0 - 7.0.6
Spring Security 6.5.0 - 6.5.11
Spring Security 6.4.0 - 6.4.18

## References
- https://spring.io/security/cve-2026-47841
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47841.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47841
