# [H] MariaDB's connector leaks the cleartext password to an MitM despite `ssl: true`

## Summary
Severity: High
Advisory: GHSA-cqhc-2h57-wpxf
CVE: CVE-2026-55215
CWE: CWE-295, CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-cqhc-2h57-wpxf
Type: github-advisory

## Affected
- npm: `mariadb` — affected >=0 <3.2.4
- npm: `mariadb` — affected >=3.3.0 <3.3.3
- npm: `mariadb` — affected >=3.4.0 <3.4.6
- npm: `mariadb` — affected >=3.5.0 <3.5.3

## Details
### Summary
When SSL/TLS is enabled but no CA / server certificate is provided, the
connector verifies the server's identity using fingerprint validation. The
check is effective,  the connection is ultimately rejected when it fails, 
but it happens *after* the authentication exchange. As a result, the
credentials are sent before validation occurs, so an active man-in-the-middle
who presents their own certificate receives the password in the handshake
before the connection is aborted.

### Impact
The credentials are transmitted to the peer before the server's identity is
validated. An on-path attacker (MitM) presenting any certificate can capture
the account password, even though the connection then fails the fingerprint
check and is closed. The disclosed credentials can subsequently be used to
authenticate directly against the server.

- Attacker requirement: active man-in-the-middle position on the network path
- Affected configuration: SSL/TLS enabled without a CA / server certificate

### Affected versions
- < 3.2.4
- 3.3.0 – 3.3.2
- 3.4.0 – 3.4.5
- 3.5.0 – 3.5.2

### Patches
Fixed in 3.2.4, 3.3.3, 3.4.6, and 3.5.3. Upgrade to one of these (or later)
on your branch.

### Workarounds
Until you can upgrade, configure certificate verification explicitly, provide
the server/CA certificate and use a verifying SSL mode (e.g. VERIFY_CA /
VERIFY_FULL). 

Reported by haaahaaahiihiiii (no GitHub account).

## References
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/security/advisories/GHSA-cqhc-2h57-wpxf
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/commit/514576a5a1fab3ea8498613e259a0b7a764e7302
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/commit/c47d7275835c78c7eb8186cd23e9d57c045c128b
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/commit/ecd36958e6e3bf0e0fa8389546f50c0ed6dbb2ac
- https://hackerone.com/reports/3777370
- https://github.com/mariadb-corporation/mariadb-connector-nodejs
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/releases/tag/3.3.3
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/releases/tag/3.4.6
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/releases/tag/3.5.3
- https://jira.mariadb.org/browse/CONJS-349
