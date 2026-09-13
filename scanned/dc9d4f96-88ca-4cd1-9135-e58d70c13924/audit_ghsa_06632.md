# [M] install: TOCTOU symlink race (unlink-then-create without O_EXCL) allows arbitrary file overwrite

## Summary
Severity: Medium
Advisory: GHSA-239g-2685-54x3
CVE: CVE-2026-35355
CWE: CWE-367, CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-239g-2685-54x3
Type: github-advisory

## Affected
- crates.io: `uu_install` — affected >=0 <0.6.0

## Details
`copy_file` in `install/src/install.rs` removes the destination then recreates it by pathname via `File::create` / `fs::copy` without `O_EXCL`/`create_new`. Between the unlink and the recreate, a local attacker with write access to the destination directory can drop in a symlink and redirect the write.

**Impact:** when `install` runs privileged into an attacker-writable directory (staging/build paths), the race allows redirecting writes to arbitrary files and overwriting sensitive system files (`/etc/passwd`, `/etc/shadow`). Recommendation: create atomically with `create_new`/`O_EXCL` and copy via the opened fd rather than reopening by path.

**Remediation:** Acknowledged by Canonical; fixed in commit b5bbabc1.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.50. Credit: Zellic._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-239g-2685-54x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-35355
- https://github.com/uutils/coreutils/pull/10067
- https://github.com/uutils/coreutils/commit/b5bbabc18a1121908848d836f869a4e98eb63886
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.6.0
