# [M] org.mariadb:r2dbc-mariadb has Inappropriate Encoding for Output Context and Improper Encoding or Escaping of Output

## Summary
Severity: Medium
Advisory: GHSA-5rqc-86vf-g8r2
CVE: CVE-2026-55859
CWE: CWE-116, CWE-838
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-5rqc-86vf-g8r2
Type: github-advisory

## Affected
- Maven: `org.mariadb:r2dbc-mariadb` — affected >=0 <1.4.1

## Details
### Summary

The connector encodes and decodes all character data assuming the connection character set is UTF-8. A server can change character_set_client mid-session to a non-UTF-8 charset, after which the driver and server interpret the same bytes under different encodings, causing silent data corruption and a client/server charset-confusion mismatch.

### Details

The driver encodes and decodes all character data on the assumption that the connection character set is UTF-8. The server can, however, announce a change of character_set_client mid-session through the OK-packet session-state-tracking mechanism, for example via a SET NAMES … run by a stored routine or trigger, by server configuration, or by a hostile server.

If the new charset is not UTF-8, the driver continues to read and write UTF-8 while the server interprets the same bytes under a different encoding. The result is silent data corruption and a client/server charset-confusion mismatch. Charset confusion of this kind is also the primitive that can defeat byte-wise quoting/escaping when client and server disagree on a multi-byte encoding.

### Am I affected?

You are affected if you use mariadb Connector/R2DBC (org.mariadb:r2dbc-mariadb) below 1.4.1 and a connection can be steered, by a hostile or man-in-the-middle server, or by server-side state such as a stored routine, trigger, or configuration — to switch character_set_client to a non-UTF-8 value mid-session.

### Impact

Silent data corruption and a client/server encoding mismatch once the connection's charset diverges from UTF-8. Because the mismatch undermines the assumption that quoting/escaping operates on UTF-8 bytes, it belongs to the charset-confusion class that can lead to SQL injection.

### Patches

Fixed in 1.4.1. Once the connection is fully initialized, any subsequent charset change to a value that is not utf8 / utf8mb3 / utf8mb4 is rejected: the driver raises R2dbcNonTransientResourceException (SQLState 08000) and closes the connection rather than continuing to exchange data under a mismatched encoding. Upgrade to 1.4.1 or later.

### Workarounds

There is no reliable application-level workaround; upgrade to 1.4.1 or later.

### Credit

Reported by Yalguun Tumenkhuu ([@fg0x0](https://github.com/fg0x0/)).

## References
- https://github.com/mariadb-corporation/mariadb-connector-r2dbc/security/advisories/GHSA-5rqc-86vf-g8r2
- https://github.com/mariadb-corporation/mariadb-connector-r2dbc/commit/38bad9afebc6c581a853656a42f9ebf403b1b1b7
- https://github.com/mariadb-corporation/mariadb-connector-r2dbc
- https://github.com/mariadb-corporation/mariadb-connector-r2dbc/releases/tag/1.4.1
- https://jira.mariadb.org/browse/R2DBC-124
