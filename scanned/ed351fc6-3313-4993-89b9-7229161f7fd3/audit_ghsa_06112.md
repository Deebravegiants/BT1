# [M] MariaDB has cleartext password disclosure to a MITM on the initial-handshake

## Summary
Severity: Medium
Advisory: GHSA-g9jj-cgmh-9f38
CVE: CVE-2026-55856
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-g9jj-cgmh-9f38
Type: github-advisory

## Affected
- Maven: `org.mariadb.jdbc:mariadb-java-client` — affected >=0 <2.7.14
- Maven: `org.mariadb.jdbc:mariadb-java-client` — affected >=3.0.0 <3.3.5
- Maven: `org.mariadb.jdbc:mariadb-java-client` — affected >=3.4.0 <3.4.3
- Maven: `org.mariadb.jdbc:mariadb-java-client` — affected >=3.5.0 <3.5.9

## Details
### Summary

When a Java application connects with sslMode=verify-full (or verify-ca) and a password but does not pin a server certificate, Connector/J deliberately accepts an untrusted/self-signed certificate at the TLS layer (the "MITM-proof without a CA" feature) and proves the server's identity afterwards by binding the certificate fingerprint into the authentication exchange. That fingerprint enforcement is applied to the OK-packet and auth-switch paths but not to the initial-handshake path. An active man-in-the-middle that presents a self-signed certificate, claims to be MariaDB, and names the initial authentication plugin mysql_clear_password receives the victim's database password in cleartext, before any fingerprint/identity check runs. The connection is torn down a moment later, but the credential is already gone.

### Details

For sslMode=verify-full/verify-ca with a password and no serverSslCert/trustStore, the connector falls back to an ephemeral trust manager (default fallbackToSystemTrustStore=true) that accepts any non-expired certificate at the TLS layer and records its fingerprint. Identity is then meant to be enforced via that fingerprint.

The enforcement guard is present on two of the three paths, the OK-packet fingerprint check and the auth-switch handler (where the clear-password plugin is only allowed when the fingerprint is already verified). It is absent on the initial-handshake send: HandshakeResponse.encode() builds the mysql_clear_password response after checking only that SSL is enabled, never consulting the recorded fingerprint, sslMode, or whether the plugin is MITM-proof. By that point the connector already knows the certificate was self-signed. The clear-password plugin does not declare itself MITM-proof (it inherits the safe default), which confirms it is meant to be refused on an unverified certificate; the initial-handshake path simply never consults that flag. The initial path also bypasses restrictedAuth.

### Impact

An active man-in-the-middle steals the full cleartext database password of any Java application using Connector/J with sslMode=verify-full/verify-ca plus a password and no pinned certificate, the configuration documented as the easy, secure default. With the captured credentials the attacker can take over the database account and read or modify all data that account is authorized for. The victim takes no unusual action; the developer explicitly enabled TLS verification expecting exactly this protection.

### Patches

Fixed in 2.7.14, 3.3.5, 3.4.3, and 3.5.9. Upgrade to the patched release on your branch (3.5.x → 3.5.9, 3.4.x → 3.4.3, 3.0/3.1/3.2/3.3.x → 3.3.5, 2.x → 2.7.14). The fix applies the same certFingerprint != null && !isMitMProof() guard to the initial-handshake path before writing the auth response, refusing to send a mysql_clear_password (or any non-MITM-proof) response on an as-yet-unverified certificate, matching the auth-switch path.

### Workarounds

If you cannot upgrade immediately, pin the server certificate (serverSslCert= the real CA / server cert). With a pinned certificate the self-signed certificate of a man-in-the-middle is rejected at the TLS layer before any password is transmitted.

Credit

Reported by haaahaaahiihiiii

## References
- https://github.com/mariadb-corporation/mariadb-connector-j/security/advisories/GHSA-g9jj-cgmh-9f38
- https://github.com/mariadb-corporation/mariadb-connector-j/commit/149ec6a626376214966c01f42d48be1b80d06056
- https://github.com/mariadb-corporation/mariadb-connector-j/commit/d90b9872322c76b05a48219be66bff1d33102f8a
- https://hackerone.com/reports/3777370
- https://github.com/mariadb-corporation/mariadb-connector-j
- https://github.com/mariadb-corporation/mariadb-connector-j/releases/tag/3.4.3
- https://github.com/mariadb-corporation/mariadb-connector-j/releases/tag/3.5.9
- https://jira.mariadb.org/browse/CONJ-1325
