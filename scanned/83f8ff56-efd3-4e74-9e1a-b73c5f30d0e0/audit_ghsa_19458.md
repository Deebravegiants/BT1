# [M] Jujutsu does not have SHA-1 collision detection

## Summary
Severity: Medium
Advisory: GHSA-794x-2rpg-rfgr
CWE: CWE-328
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-794x-2rpg-rfgr
Type: github-advisory

## Affected
- crates.io: `jj-lib` — affected >=0 <0.28.1
- crates.io: `jj-cli` — affected >=0 <0.28.1

## Details
### Summary
Jujutsu 0.28.0 and earlier rely on versions of gitoxide that use SHA-1 hash implementations without any collision detection, leaving them vulnerable to hash collision attacks.

### Details
This is a result of the underlying [CVE-2025-31130 / GHSA-2frx-2596-x5r6](https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-2frx-2596-x5r6) vulnerability in the gitoxide library Jujutsu uses to interact with Git repositories; see that advisory for technical details. This separate advisory is being issued due to the downstream impact on users of Jujutsu.

### Impact
An attacker with the ability to mount a collision attack on SHA-1 like the [SHAttered](https://shattered.io/) or [SHA-1 is a Shambles](https://sha-mbles.github.io/) attacks could create two distinct Git objects with the same hash. This is becoming increasingly affordable for well‐resourced attackers, with the Shambles researchers in 2020 estimating $45k for a chosen‐prefix collision or $11k for a classical collision, and projecting less than $10k for a chosen‐prefix collision by 2025. The result could be used to disguise malicious repository contents, or potentially exploit assumptions in Jujutsu’s logic to cause further vulnerabilities.

## References
- https://github.com/jj-vcs/jj/security/advisories/GHSA-794x-2rpg-rfgr
- https://github.com/jj-vcs/jj/commit/350da7d013773377aec0d3a4bf4374d3c941460e
- https://github.com/jj-vcs/jj
