# [H] OpenVM allows the byte decomposition of pc in AUIPC chip to overflow

## Summary
Severity: High
Advisory: GHSA-jf2r-x3j4-23m7
CVE: CVE-2025-46723
CWE: CWE-131
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-05
Source: https://github.com/advisories/GHSA-jf2r-x3j4-23m7
Type: github-advisory

## Affected
- crates.io: `openvm` — affected >=1.0.0 <1.1.0

## Details
The fix to https://cantina.xyz/code/c486d600-bed0-4fc6-aed1-de759fd29fa2/findings/21 has a typo that still results in the highest limb of `pc` being range checked to 8-bits instead of 6-bits.

In the AIR, we do https://github.com/openvm-org/openvm/blob/0f94c8a3dfa7536c1231465d1bdee5fc607a5993/extensions/rv32im/circuit/src/auipc/core.rs#L135
```
        for (i, limb) in pc_limbs.iter().skip(1).enumerate() {
            if i == pc_limbs.len() - 1 {
```

It should be
```
        for (i, limb) in pc_limbs.iter().enumerate().skip(1) {
```

Right now the if statement is never triggered because the enumeration gives `i=0,1,2` when we instead want `i=1,2,3`. What this means is that `pc_limbs[3]` is range checked to 8-bits instead of 6-bits.

This leads to a vulnerability where the `pc_limbs` decomposition differs from the true `pc`, which means a malicious prover can make the destination register take a different value than the AUIPC instruction dictates, by making the decomposition overflow the BabyBear field.

## References
- https://github.com/openvm-org/openvm/security/advisories/GHSA-jf2r-x3j4-23m7
- https://nvd.nist.gov/vuln/detail/CVE-2025-46723
- https://github.com/openvm-org/openvm/commit/68da4b50c033da5603517064aa0a08e1bbf70a01
- https://cantina.xyz/code/c486d600-bed0-4fc6-aed1-de759fd29fa2/findings/21
- https://github.com/openvm-org/openvm
- https://github.com/openvm-org/openvm/blob/0f94c8a3dfa7536c1231465d1bdee5fc607a5993/extensions/rv32im/circuit/src/auipc/core.rs#L135
- https://github.com/openvm-org/openvm/releases/tag/v1.1.0
