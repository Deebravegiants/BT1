# [H] HAProxy - NULL Pointer Dereference in hpack_dht_insert Function

## Summary
Severity: High
Advisory: BIT-haproxy-2026-55204
Aliases: CVE-2026-55204
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-haproxy-2026-55204
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=0 <3.4.1

## Details
HAProxy through  3.4.0, fixed in commit 9a6d1fe, contains a null pointer dereference vulnerability in hpack_dht_insert() within src/hpack-tbl.c that fails to validate the return value of hpack_dht_defrag() when the memory pool is exhausted. An attacker can trigger HPACK dynamic table insertions under memory pressure to dereference a NULL pointer and crash HAProxy worker processes, causing denial of service.

## References
- https://github.com/haproxy/haproxy/commit/9a6d1fe3f00d86ab4ea6ea6ea0a5d48fc058a513
- https://nvd.nist.gov/vuln/detail/CVE-2026-55204
- https://www.vulncheck.com/advisories/haproxy-null-pointer-dereference-in-hpack-dht-insert-function
