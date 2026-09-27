# [H] CVE-2026-37552

## Summary
Severity: High
Advisory: CVE-2026-37552
CVSS: 8.4 (CVSS:3.1/AC:L/AV:L/A:H/C:H/I:H/PR:N/S:U/UI:N)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-37552
Type: osv

## Details
Unsafe deserialization vulnerability in MixPHP Framework 2.x thru 2.2.17. The sync-invoke TCP server (Server.php:87) receives data from a TCP socket, passes it directly to Opis\Closure\unserialize(), then executes the result via call_user_func(). No authentication or signature verification exists on the TCP connection. An attacker with access to the localhost TCP port (server binds 127.0.0.1) can send a crafted serialized PHP closure to achieve arbitrary code execution.

## References
- https://gist.github.com/sgInnora/fa46386840fe978a30d7e53c458f2975
- https://github.com/mix-php/mix/blob/v2.2.17/src/sync-invoke/src/Server.php
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37552.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-37552
- https://github.com/mix-php/mix
