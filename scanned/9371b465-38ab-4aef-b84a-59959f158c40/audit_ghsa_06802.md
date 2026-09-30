# [H] mkfifo: permissions of an existing file are changed after FIFO creation fails

## Summary
Severity: High
Advisory: GHSA-pmf6-rcx4-v53v
CVE: CVE-2026-35341
CWE: CWE-281, CWE-732
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-pmf6-rcx4-v53v
Type: github-advisory

## Affected
- crates.io: `uu_mkfifo` — affected >=0 <0.6.0

## Details
When `mkfifo()` fails (e.g. target already exists), the code shows an error but is missing a `continue;`, so it falls through to `fs::set_permissions` and changes the permissions of the pre-existing file to the default FIFO mode (`0o666` & umask -> `0644`).

```
$ touch secret; chmod 000 secret
$ coreutils mkfifo secret fifo3 fifo4
mkfifo: cannot create fifo 'secret': File exists
$ ll secret      # uutils:
prw-r--r-- secret   # changed to 644 (GNU leaves it 000)
```

**Impact:** an attacker (or user error) can relax permissions on sensitive owner-only files such as SSH private keys, exposing them to other users. Recommendation: add `continue;` after the error.

**Remediation:** Acknowledged by Canonical; fixed in PR #10376.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.8. Credit: Zellic._

_Upstream tracking issue: https://github.com/uutils/coreutils/issues/10020 · CVE-2026-35341_

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-pmf6-rcx4-v53v
- https://nvd.nist.gov/vuln/detail/CVE-2026-35341
- https://github.com/uutils/coreutils/issues/10020
- https://github.com/uutils/coreutils/pull/10376
- https://github.com/uutils/coreutils
