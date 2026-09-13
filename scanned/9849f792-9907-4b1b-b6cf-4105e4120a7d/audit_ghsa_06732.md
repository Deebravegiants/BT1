# [M] cp: -R reads device nodes as streams, destroying device semantics

## Summary
Severity: Medium
Advisory: GHSA-8vrf-r662-2w2v
CVE: CVE-2026-35358
CWE: CWE-400, CWE-706
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-8vrf-r662-2w2v
Type: github-advisory

## Affected
- crates.io: `uu_cp` — affected >=0 <0.7.0

## Details
The cp utility in uutils coreutils, when performing recursive copies (-R), incorrectly treats character and block device nodes as stream sources rather than preserving them. Because the implementation reads bytes into regular files at the destination instead of using mknod, device semantics are destroyed (e.g., /dev/null becomes a regular file). This behavior can lead to runtime denial of service through disk exhaustion or process hangs when reading from unbounded device nodes.

---
_Zellic finding 3.53. Reported in the Zellic *uutils coreutils Program Security Assessment* (for Canonical, Jan 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-8vrf-r662-2w2v
- https://nvd.nist.gov/vuln/detail/CVE-2026-35358
- https://github.com/uutils/coreutils/issues/9746
- https://github.com/uutils/coreutils/pull/11163
- https://github.com/uutils/coreutils/commit/e6a3bb596f149628ba973eec3d099f3bb69f2464
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.7.0
