# [M] org.mariadb:r2dbc-mariadb vulnerable to cleartext password disclosure to a man-in-the-middle server (clear-text auth plugins not gated on a secure transport)

## Summary
Severity: Medium
Advisory: GHSA-c857-9x2m-cvh2
CVE: CVE-2026-55860
CWE: CWE-319, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-c857-9x2m-cvh2
Type: github-advisory

## Affected
- Maven: `org.mariadb:r2dbc-mariadb` — affected >=0 <1.4.1

## Details
### Summary

The connector does not gate clear-text password authentication plugins on transport encryption. A hostile or man-in-the-middle MariaDB server can request a clear-text plugin over an unencrypted (plain-TCP) connection, and the driver responds with the user's password in cleartext on the wire.

### Details

The driver does not require a secure transport before using clear-text-password authentication plugins. A hostile or man-in-the-middle server can issue an AuthSwitchRequest naming mysql_clear_password or dialog (PAM) over a plain-TCP, unencrypted connection, and the driver replies with the user's password as cleartext bytes on the wire.

The root cause is that the AuthenticationPlugin interface declares no capability for a plugin to require a secure connection. Because no such gate exists, clear-text plugins run regardless of whether the connection is encrypted.

### Impact

The account password is transmitted in cleartext to the peer. An on-path attacker (MITM) who presents themselves as the server can capture the password during the authentication handshake. The disclosed credentials can subsequently be used to authenticate directly against the database server.

### Patches

Fixed in 1.4.1. Clear-text authentication plugins (mysql_clear_password, dialog/PAM) now require a secure connection: the AuthenticationPlugin contract can declare that a plugin requires a secure transport, and such plugins are permitted only over an encrypted connection. Upgrade to 1.4.1 or later.

### Workarounds

Until you can upgrade, configure certificate verification explicitly: provide the server/CA certificate and use a verifying SSL mode (e.g. VERIFY_CA / VERIFY_FULL) so the connection is encrypted and the server's identity is established before credentials are sent.

### Credit

Reported by Yalguun Tumenkhuu ([@fg0x0](https://github.com/fg0x0/)).

## References
- https://github.com/mariadb-corporation/mariadb-connector-r2dbc/security/advisories/GHSA-c857-9x2m-cvh2
- https://github.com/mariadb-corporation/mariadb-connector-r2dbc/commit/be786603ec5530414996d2396157013e095b320a
- https://hackerone.com/reports/3784556
- https://github.com/mariadb-corporation/mariadb-connector-r2dbc
- https://github.com/mariadb-corporation/mariadb-connector-r2dbc/releases/tag/1.4.1
- https://jira.mariadb.org/browse/R2DBC-115
