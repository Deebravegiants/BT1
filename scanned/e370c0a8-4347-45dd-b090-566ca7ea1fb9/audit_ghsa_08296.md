# [M] Shamefile has an arbitrary file read via shamefile.yaml in shame next

## Summary
Severity: Medium
Advisory: GHSA-x6p3-76f2-xxvh
CVE: CVE-2026-47144
CWE: CWE-22
Ecosystem: PyPI, crates.io, npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-x6p3-76f2-xxvh
Type: github-advisory

## Affected
- PyPI: `shamefile` — affected >=0 <0.1.7
- npm: `shamefile` — affected >=0 <0.1.7
- crates.io: `shamefile` — affected >=0 <0.1.7

## Details
### Impact

A path traversal vulnerability in `shame next` allows an attacker-controlled `shamefile.yaml` to disclose contents of files outside the repository, one line at a time, to the terminal of a user who runs the command. See patch commit for technical details.

### Patches

Fixed in 0.1.7. Upgrade to either 0.1.7 or later versions to incorporate the patch.

### Workarounds

Do not run `shame next` against untrusted `shamefile.yaml`. Use `shame me --dry-run` for CI validation.

### Resources

- Patch commit: https://github.com/BKDDFS/shamefile/commit/77b0aeea318503582818c708518c601fedc43557
- Pull request: https://github.com/BKDDFS/shamefile/pull/80
- Release: https://github.com/BKDDFS/shamefile/releases/tag/v0.1.7
- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html)

## References
- https://github.com/BKDDFS/shamefile/security/advisories/GHSA-x6p3-76f2-xxvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-47144
- https://github.com/BKDDFS/shamefile/pull/80
- https://github.com/BKDDFS/shamefile/commit/77b0aeea318503582818c708518c601fedc43557
- https://github.com/BKDDFS/shamefile
- https://github.com/BKDDFS/shamefile/releases/tag/v0.1.7
- https://github.com/pypa/advisory-database/tree/main/vulns/shamefile/PYSEC-2026-3065.yaml
