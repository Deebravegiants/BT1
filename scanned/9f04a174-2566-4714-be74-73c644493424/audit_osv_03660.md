# [H] ALPINE-CVE-2026-40164

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-40164
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40164
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. Before commit 0c7d133c3c7e37c00b6d46b658a02244fdd3c784, jq used MurmurHash3 with a hardcoded, publicly visible seed (0x432A9843) for all JSON object hash table operations, which allowed an attacker to precompute key collisions offline. By supplying a crafted JSON object (~100 KB) where all keys hashed to the same bucket, hash table lookups degraded from O(1) to O(n), turning any jq expression into an O(n²) operation and causing significant CPU exhaustion. This affected common jq use cases such as CI/CD pipelines, web services, and data processing scripts, and was far more practical to exploit than existing heap overflow issues since it required only a small payload. This issue has been patched in commit 0c7d133c3c7e37c00b6d46b658a02244fdd3c784.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40164
