# [M] kill: 'kill -1' parsed as PID -1, sending SIGTERM to all processes (system crash / DoS)

## Summary
Severity: Medium
Advisory: GHSA-p6rv-2qpm-fwvg
CVE: CVE-2026-35369
CWE: CWE-20, CWE-754
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-p6rv-2qpm-fwvg
Type: github-advisory

## Affected
- crates.io: `uu_kill` — affected >=0 <0.6.0

## Details
`kill -1` is incorrectly parsed as a positional `pid = -1`; combined with the default SIGTERM this calls `kill(-1, SIGTERM)`, signaling nearly every process the caller can see. GNU `kill` recognizes `-1`/`-9` as signals and reports "not enough arguments".

```
$ kill -1        # uutils: kill(-1, SIGTERM) -> mass termination / crash
$ kill -1        # GNU: kill: not enough arguments
```

**Impact:** a user running `kill -1` mass-terminates processes, potentially crashing the system. Recommendation: parse `-N` as a signal number, and error with "not enough arguments" when no PID is given.

**Remediation:** Acknowledged by Canonical; fixed in commit cae94028.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.70. Credit: Zellic._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-p6rv-2qpm-fwvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35369
- https://github.com/uutils/coreutils/pull/9700
- https://github.com/uutils/coreutils/commit/2d3aebce6712841bc08b9b94e9078be50a25fc10
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.6.0
