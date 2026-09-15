# [H] Coturn: Format String Injection via TURN USERNAME/REALM into hiredis Redis Command

## Summary
Severity: High
Advisory: CVE-2026-68553
Aliases: GHSA-4g7c-p5wg-j4hp
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-68553
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.13.0, an authenticated TURN user can place printf-style format specifiers in the STUN USERNAME or REALM attribute, which passes is_secure_string() validation and is embedded into Redis keys at nine call sites in src/apps/relay/ns_ioalib_engine_impl.c. send_message_to_redis() in src/apps/relay/hiredis_libevent2.c then passes the attacker-controlled key as the format argument to redisAsyncCommand() while supplying only one variadic value, causing hiredis redisvFormatCommand() to read past the va_list. Exploitation can crash the coturn process and terminate active TURN sessions or disclose stack memory into Redis. This issue is fixed in version 4.13.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.13.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68553.json
- https://github.com/coturn/coturn/security/advisories/GHSA-4g7c-p5wg-j4hp
- https://nvd.nist.gov/vuln/detail/CVE-2026-68553
- https://github.com/coturn/coturn/commit/8fa38032bb4751e11e072d65a8eca3c06c950979
