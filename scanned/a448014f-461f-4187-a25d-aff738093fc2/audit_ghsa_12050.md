# [M] Picomatch: Method Injection in POSIX Character Classes causes incorrect Glob Matching

## Summary
Severity: Medium
Advisory: GHSA-3v7f-55p6-f55p
CVE: CVE-2026-33672
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-3v7f-55p6-f55p
Type: github-advisory

## Affected
- npm: `picomatch` — affected >=4.0.0 <4.0.4
- npm: `picomatch` — affected >=3.0.0 <3.0.2
- npm: `picomatch` — affected >=0 <2.3.2

## Details
### Impact
picomatch is vulnerable to a **method injection vulnerability (CWE-1321)** affecting the `POSIX_REGEX_SOURCE` object. Because the object inherits from `Object.prototype`, specially crafted POSIX bracket expressions (e.g., `[[:constructor:]]`) can reference inherited method names. These methods are implicitly converted to strings and injected into the generated regular expression.

This leads to **incorrect glob matching behavior (integrity impact)**, where patterns may match unintended filenames. The issue does **not enable remote code execution**, but it can cause security-relevant logic errors in applications that rely on glob matching for filtering, validation, or access control.

All users of affected `picomatch` versions that process untrusted or user-controlled glob patterns are potentially impacted.

### Patches

This issue is fixed in picomatch 4.0.4, 3.0.2 and 2.3.2.

Users should upgrade to one of these versions or later, depending on their supported release line.

### Workarounds

If upgrading is not immediately possible, avoid passing untrusted glob patterns to picomatch.

Possible mitigations include:
- Sanitizing or rejecting untrusted glob patterns, especially those containing POSIX character classes like `[[:...:]]`.
- Avoiding the use of POSIX bracket expressions if user input is involved.
- Manually patching the library by modifying `POSIX_REGEX_SOURCE` to use a null prototype:

  ```js
  const POSIX_REGEX_SOURCE = {
    __proto__: null,
    alnum: 'a-zA-Z0-9',
    alpha: 'a-zA-Z',
    // ... rest unchanged
  };
  
### Resources

- fix for similar issue: https://github.com/micromatch/picomatch/pull/144
- picomatch repository https://github.com/micromatch/picomatch

## References
- https://github.com/micromatch/picomatch/security/advisories/GHSA-3v7f-55p6-f55p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33672
- https://github.com/micromatch/picomatch/commit/4516eb521f13a46b2fe1a1d2c9ef6b20ddc0e903
- https://github.com/micromatch/picomatch
