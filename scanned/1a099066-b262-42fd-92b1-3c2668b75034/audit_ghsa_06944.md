# [M] chmod: recursive mode returns exit code 0 even when some files fail (last-file-wins)

## Summary
Severity: Medium
Advisory: GHSA-4x34-chg5-mwjj
CVE: CVE-2026-35339
CWE: CWE-252, CWE-253, CWE-755
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-4x34-chg5-mwjj
Type: github-advisory

## Affected
- crates.io: `uu_chmod` — affected >=0 <0.6.0

## Details
In `Chmoder::chmod()` the recursive branch overwrites the running result instead of accumulating it, so the exit code reflects only the *last* file processed:

```
if self.recursive {
    r = self.walk_dir_with_context(file, true);   // overwrites r
} else {
    r = self.chmod_file(file).and(r);
}
```

**PoC:** GNU returns 1 when a file fails; uutils returns 0 if the last entry succeeds:

```
$ chmod -R 0755 chmod-bug/root chmod-bug/user  # GNU -> ret=1
$ uutils chmod -R 0755 chmod-bug/root chmod-bug/user  # -> ret=0
```

**Impact:** scripts relying on the exit code get a false success signal while some files retained restrictive/unexpected permissions, leading to access-control misconfigurations. Recommendation: accumulate errors during traversal.

**Remediation:** Acknowledged by Canonical; fixed in commit abd581f6.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.2. Credit: Zellic._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-4x34-chg5-mwjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-35339
- https://github.com/uutils/coreutils/pull/9793
- https://github.com/uutils/coreutils/commit/abd581f62e97d0b147306ac40eac13af71c6fbba
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.6.0
