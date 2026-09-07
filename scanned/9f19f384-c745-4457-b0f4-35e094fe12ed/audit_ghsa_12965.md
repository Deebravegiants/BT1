# [H] Keylime's registrar vulnerable to Denial-of-service attack via a single open connection

## Summary
Severity: High
Advisory: GHSA-pg75-v6fp-8q59
CVE: CVE-2023-38200
CWE: CWE-834
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-01
Source: https://github.com/advisories/GHSA-pg75-v6fp-8q59
Type: github-advisory

## Affected
- PyPI: `keylime` — affected >=0 <7.4.0

## Details
### Impact
Keylime `registrar` is prone to a simple denial of service attack in which an adversary opens a connection to the TLS port (by default, port `8891`) blocking further, legitimate connections. As long as the connection is open, the `registrar` is blocked and cannot serve any further clients (`agents` and `tenants`), which prevents normal operation. The problem does not affect the `verifier`.

### Patches
Users should upgrade to release 7.4.0

## References
- https://github.com/keylime/keylime/security/advisories/GHSA-pg75-v6fp-8q59
- https://nvd.nist.gov/vuln/detail/CVE-2023-38200
- https://github.com/keylime/keylime/pull/1421
- https://github.com/keylime/keylime/commit/c68d8f0b7ea549c12b6956ab0f3c28ae0360ae17
- https://access.redhat.com/security/cve/CVE-2023-38200
- https://bugzilla.redhat.com/show_bug.cgi?id=2222692
- https://github.com/keylime/keylime
- https://github.com/keylime/keylime/releases/tag/v7.4.0
