# [C] Dep Group Remote Memory Exhaustion (Denial of Service)

## Summary
Severity: Critical
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2022-04-12
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-j35p-q24r-5367
Type: github-advisory

## Details
### Impact
A remote attacker could exploit this vulnerability to exhaust ckb process memory of an affected node.

### Patches
Upgrade to 0.43.1 or later.

### References
After resolving the outpoints of one dep group, we put the corresponding content into a vec ( https://github.com/nervosnetwork/ckb/blob/v0.42.0/util/types/src/core/cell.rs#L600-L617 ), there is a vulnerability to a memory dos attack because there is no determination of whether the outpoints is duplicated.

PoC:
```
before send dos tx rss:
105700

after rss:
2306932
```

DoS cost: 25.6 KB * 150 + dep_tx out_points capacity ( 36 * 150 * 100 = 540000 ) = 4380000 CKB
Send 50 dos_tx, memory exhausted: (25.6 KB * 150  * 100) * 50 = 19.2 GB
