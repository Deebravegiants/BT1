# [H] jq: Algorithmic complexity DoS via hardcoded MurmurHash3 seed

## Summary
Severity: High
Advisory: CVE-2026-40164
Aliases: GHSA-wwj8-gxm6-jc29
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-40164
Type: osv

## Details
jq is a command-line JSON processor. Before commit 0c7d133c3c7e37c00b6d46b658a02244fdd3c784, jq used MurmurHash3 with a hardcoded, publicly visible seed (0x432A9843) for all JSON object hash table operations, which allowed an attacker to precompute key collisions offline. By supplying a crafted JSON object (~100 KB) where all keys hashed to the same bucket, hash table lookups degraded from O(1) to O(n), turning any jq expression into an O(n²) operation and causing significant CPU exhaustion. This affected common jq use cases such as CI/CD pipelines, web services, and data processing scripts, and was far more practical to exploit than existing heap overflow issues since it required only a small payload. This issue has been patched in commit 0c7d133c3c7e37c00b6d46b658a02244fdd3c784.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40164.json
- https://access.redhat.com/errata/RHSA-2026:16252
- https://access.redhat.com/errata/RHSA-2026:16692
- https://access.redhat.com/errata/RHSA-2026:16693
- https://access.redhat.com/errata/RHSA-2026:18040
- https://access.redhat.com/errata/RHSA-2026:18042
- https://access.redhat.com/errata/RHSA-2026:18043
- https://access.redhat.com/errata/RHSA-2026:18044
- https://access.redhat.com/errata/RHSA-2026:18045
- https://access.redhat.com/errata/RHSA-2026:18046
- https://access.redhat.com/errata/RHSA-2026:18047
- https://access.redhat.com/errata/RHSA-2026:18048
- https://access.redhat.com/errata/RHSA-2026:19151
- https://access.redhat.com/errata/RHSA-2026:19365
- https://access.redhat.com/errata/RHSA-2026:23233
- https://access.redhat.com/errata/RHSA-2026:23245
- https://access.redhat.com/errata/RHSA-2026:25044
- https://access.redhat.com/errata/RHSA-2026:25096
- https://access.redhat.com/errata/RHSA-2026:25181
- https://access.redhat.com/errata/RHSA-2026:26528
