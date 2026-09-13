# [M] MariaDB has  possible SQL injection in Buffer parameter escaping under big5/gbk/sjis/cp932/gb18030 client charsets

## Summary
Severity: Medium
Advisory: GHSA-g5xc-5w98-jfvm
CVE: CVE-2026-55855
CWE: CWE-116, CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-g5xc-5w98-jfvm
Type: github-advisory

## Affected
- npm: `mariadb` — affected >=0 <3.2.4
- npm: `mariadb` — affected >=3.3.0 <3.3.4
- npm: `mariadb` — affected >=3.4.0 <3.4.6
- npm: `mariadb` — affected >=3.5.0 <3.5.3

## Details
### Summary

A SQL injection is possible when the connector escapes Buffer parameters client-side under a multi-byte client character set whose trail-byte range overlaps the ASCII backslash (0x5C): big5, gbk, sjis, cp932, and gb18030. Under these charsets, an attacker-controlled lead byte can absorb the escape byte the connector inserts, leaving the following quote unescaped so it terminates the string literal and injected SQL is parsed.

### Details

When binding a Buffer (binary) parameter, the connector escapes the value byte-by-byte, inserting a backslash (0x5C) before quote (0x27) and backslash bytes. This is correct under single-byte and UTF-8–family charsets, but unsafe under client charsets whose multi-byte trail-byte range includes 0x5C.

On the server, the SQL lexer performs multi-byte character recognition (my_ismbchar) before it interprets escape sequences. If character_set_client is one of the affected charsets and the attacker controls a byte the lexer treats as a valid lead byte, the sequence <lead-byte><0x5C> is consumed as a single multi-byte character. The escaping backslash inserted by the connector is swallowed as that character's trail byte, so the following 0x27 is no longer escaped — it closes the string literal, and the remaining bytes are parsed as SQL.

This is the well-known multi-byte escaping bypass (the same class that historically affected addslashes / mysql_real_escape_string under GBK/Big5), here applied to the connector's client-side Buffer escaping path.

### Am I affected?

You are affected if all of the following hold:


You use mariadb Connector/Node.js at a version below the patched releases listed below.
The connection's client character set is one of big5, gbk, sjis, cp932, or gb18030. This is not the default (the default is utf8mb4).
Untrusted data can reach a Buffer-typed query parameter.


Applications using utf8mb4 (or any charset whose trail-byte range does not include 0x5C) are not affected by this vector. Parameters bound through the binary/server-side prepared-statement path are also not affected, because those values are sent out-of-band and are never escaped into the SQL text.

### Impact

SQL injection. An attacker able to influence the contents of a Buffer parameter can break out of the intended string literal and inject arbitrary SQL, leading to unauthorized read or modification of data and, depending on the database account's privileges, further compromise.

### Patches

Fixed in 3.2.4, 3.3.3, 3.4.6, and 3.5.3. Upgrade to the patched release on your branch:


* 3.5.x → 3.5.3
* 3.4.x → 3.4.6
* 3.3.x → 3.3.3
* 3.2.x and earlier → 3.2.4 (or any newer release)


### Workarounds

If you cannot upgrade immediately:

Use server-side prepared statements (execute) so parameters are bound via the binary protocol rather than escaped into the SQL text.
Avoid passing untrusted data as Buffer parameters under the affected charsets.


Credit

Reported by Yalguun Tumenkhuu ([@fg0x0](https://github.com/fg0x0/)).

## References
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/security/advisories/GHSA-g5xc-5w98-jfvm
- https://github.com/mariadb-corporation/mariadb-connector-nodejs/commit/0148cadba48064d430902678bbc5b4b62dc1c04f
- https://github.com/mariadb-corporation/mariadb-connector-nodejs
- https://jira.mariadb.org/browse/CONJS-350
