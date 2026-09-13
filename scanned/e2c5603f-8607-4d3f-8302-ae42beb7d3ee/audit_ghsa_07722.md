# [H] Improper Digest Verification in httpsig-hyper May Allow Message Integrity Bypass

## Summary
Severity: High
Advisory: GHSA-7v42-g35v-xrch
CVE: CVE-2026-26275
CWE: CWE-354, CWE-697
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-7v42-g35v-xrch
Type: github-advisory

## Affected
- crates.io: `httpsig-hyper` — affected >=0 <0.0.23

## Details
### Impact

An issue was discovered in `httpsig-hyper` where Digest header verification could incorrectly succeed due to misuse of Rust's `matches!` macro. Specifically, the comparison:

```rust
if matches!(digest, _expected_digest)
```

treated `_expected_digest` as a pattern binding rather than a value comparison, resulting in unconditional success of the match expression.

As a consequence, digest verification could incorrectly return success even when the computed digest did not match the expected value.

Applications relying on Digest verification as part of HTTP message signature validation may therefore fail to detect message body modification. The severity depends on how the library is integrated and whether additional signature validation layers are enforced.

---

### Patches

This issue has been fixed in:

- `httpsig-hyper` >= 0.0.23

The fix replaces the incorrect `matches!` usage with proper value comparison and additionally introduces constant-time comparison for digest verification as defense-in-depth.

Regression tests have also been added to prevent reintroduction of this issue. Users are strongly advised to upgrade to the patched version.

---

### Workarounds

There is no reliable workaround without upgrading. Users who cannot immediately upgrade should avoid relying solely on Digest verification for message integrity and ensure that full HTTP message signature verification is enforced at the application layer.

---

### References

- PR: https://github.com/junkurihara/httpsig-rs/pull/14
- Follow-up hardening and test additions: https://github.com/junkurihara/httpsig-rs/pull/15

## References
- https://github.com/junkurihara/httpsig-rs/security/advisories/GHSA-7v42-g35v-xrch
- https://nvd.nist.gov/vuln/detail/CVE-2026-26275
- https://github.com/junkurihara/httpsig-rs/pull/14
- https://github.com/junkurihara/httpsig-rs/pull/15
- https://github.com/junkurihara/httpsig-rs/commit/5533f596c650377e02f4aa9e3eb8dba591b87370
- https://github.com/junkurihara/httpsig-rs/commit/65cbd19b395180a4bba09a89746c4b14ccb8d297
- https://github.com/junkurihara/httpsig-rs
