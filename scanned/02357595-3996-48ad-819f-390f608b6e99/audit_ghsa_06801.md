# [H] chmod: --preserve-root bypassed by any path that resolves to root (e.g. /../)

## Summary
Severity: High
Advisory: GHSA-4c7q-4928-8445
CVE: CVE-2026-35338
CWE: CWE-22, CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-4c7q-4928-8445
Type: github-advisory

## Affected
- crates.io: `uu_chmod` — affected >=0 <0.6.0

## Details
`Chmoder::chmod()` only compares the literal argument against `Path::new("/")`, so the `--preserve-root` guard is bypassed by any path that *resolves* to root — a symlink to `/` or simply `/../`.

```
if self.recursive && self.preserve_root && file == Path::new("/") {
    return Err(ChmodError::PreserveRoot("/".to_string()).into());
}
```

**PoC** — recursively chmods the entire filesystem to `000` despite `--preserve-root`:

```
chmod -R --preserve-root 000 /../ -v
```

**Impact:** `--preserve-root` is the documented safeguard against destructive recursive operations on `/`. Bypassing it allows `chmod -R` to alter permissions across the whole filesystem, causing a complete system breakdown. Recommendation: canonicalize the target path before comparing against root.

**Remediation:** Acknowledged by Canonical; fixed in commit 413055b3.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.1. Credit: Zellic._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-4c7q-4928-8445
- https://nvd.nist.gov/vuln/detail/CVE-2026-35338
- https://github.com/uutils/coreutils/pull/10033
- https://github.com/uutils/coreutils/commit/413055b378fa6fe2299c5e5f538c8e6e841ab810
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.6.0
