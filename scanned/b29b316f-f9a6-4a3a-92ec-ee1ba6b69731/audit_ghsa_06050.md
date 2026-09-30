# [M] org.mariadb.jdbc:mariadb-java-client has Inappropriate Encoding for Output Context

## Summary
Severity: Medium
Advisory: GHSA-xvr9-35cr-46v9
CVE: CVE-2026-55858
CWE: CWE-838
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-xvr9-35cr-46v9
Type: github-advisory

## Affected
- Maven: `org.mariadb.jdbc:mariadb-java-client` — affected >=0 <2.7.14
- Maven: `org.mariadb.jdbc:mariadb-java-client` — affected >=3.0.0 <3.3.5
- Maven: `org.mariadb.jdbc:mariadb-java-client` — affected >=3.4.0 <3.4.3
- Maven: `org.mariadb.jdbc:mariadb-java-client` — affected >=3.5.0 <3.5.9

## Details
### Summary

The connector encodes and decodes all character data assuming the connection character set is UTF-8. A server can change character_set_client mid-session to a non-UTF-8 charset, after which the driver and server interpret the same bytes under different encodings, causing silent data corruption and a client/server charset-confusion mismatch.

### Details

The driver encodes and decodes all character data on the assumption that the connection character set is UTF-8. 
Charset can be changed by commands like SET NAMES... commands.

If the new charset is not UTF-8, the driver continues to read and write UTF-8 while the server interprets the same bytes under a different encoding. The result is silent data corruption and a client/server charset-confusion mismatch. Charset confusion of this kind is also the primitive that can defeat byte-wise quoting/escaping when client and server disagree on a multi-byte encoding.

### Impact

Silent data corruption and a client/server encoding mismatch once the connection's charset diverges from UTF-8. Because the mismatch undermines the assumption that quoting/escaping operates on UTF-8 bytes, it belongs to the charset-confusion class that can lead to SQL injection.

### Patches

Fixed in 2.7.14, 3.3.5, 3.4.3, and 3.5.9. Upgrade to the patched release on your branch (3.5.x → 3.5.9, 3.4.x → 3.4.3, 3.0/3.1/3.2/3.3.x → 3.3.5, 2.x → 2.7.14). Once the connection is fully initialized, any subsequent charset change to a value that is not utf8 / utf8mb3 / utf8mb4 is rejected: the driver raises a SQLException with SQLState 08000 (connection exception) and closes the connection rather than continuing to exchange data under a mismatched encoding.

### Workarounds

There is no reliable application-level workaround.

### Credit

Reported by Yalguun Tumenkhuu ([@fg0x0](https://github.com/fg0x0/)).

## References
- https://github.com/mariadb-corporation/mariadb-connector-j/security/advisories/GHSA-xvr9-35cr-46v9
- https://github.com/mariadb-corporation/mariadb-connector-j/commit/300716bef1e1d0370a41be7863b88aa2d55fbb69
- https://github.com/mariadb-corporation/mariadb-connector-j/commit/7b3c69221b5463ee03472654040b3f6b9e5329c7
- https://github.com/mariadb-corporation/mariadb-connector-j/commit/8cfd9df697372ad4ed09fe87a34b34babb6d43d6
- https://github.com/mariadb-corporation/mariadb-connector-j/commit/c555c9b477521be0c35c3a5461f9f46681553607
- https://github.com/mariadb-corporation/mariadb-connector-j
- https://github.com/mariadb-corporation/mariadb-connector-j/releases/tag/2.7.14
- https://github.com/mariadb-corporation/mariadb-connector-j/releases/tag/3.3.5
- https://github.com/mariadb-corporation/mariadb-connector-j/releases/tag/3.4.3
- https://github.com/mariadb-corporation/mariadb-connector-j/releases/tag/3.5.9
- https://jira.mariadb.org/browse/CONJ-1317
