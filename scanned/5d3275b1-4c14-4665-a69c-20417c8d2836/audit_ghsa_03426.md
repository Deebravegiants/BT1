# [M] [thi.ng/egf] Potential arbitrary code execution of `#gpg`-tagged property values

## Summary
Severity: Medium
Advisory: GHSA-rj44-gpjc-29r7
CVE: CVE-2021-21412
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-rj44-gpjc-29r7
Type: github-advisory

## Affected
- npm: `@thi.ng/egf` — affected >=0 <0.4.0

## Details
### Impact

Potential for arbitrary code execution in `#gpg`-tagged property values (only if `decrypt: true` option is enabled)

### Patches

[A fix](https://github.com/thi-ng/umbrella/commit/3e14765d6bfd8006742c9e7860bc7d58ae94dfa5) has already been released as v0.4.0

### Workarounds

By default, EGF parse functions do NOT attempt to decrypt values (since GPG is only available in non-browser env).

However, if GPG encrypted values are used/required:

1. Perform a regex search for `#gpg`-tagged values in the EGF source file/string and check for backtick (\`) chars in the encrypted value string
2. Replace/remove them or skip parsing if present...

### References

https://github.com/thi-ng/umbrella/security/advisories/GHSA-rj44-gpjc-29r7#advisory-comment-65261

### For more information

If you have any questions or comments about this advisory, please open an issue in the [thi.ng/umbrella repo](https://github.com/thi-ng/umbrella/issues), of which this package is part of.

## References
- https://github.com/thi-ng/umbrella/security/advisories/GHSA-rj44-gpjc-29r7
- https://nvd.nist.gov/vuln/detail/CVE-2021-21412
- https://github.com/thi-ng/umbrella/commit/88f61656e5f5cfba960013b8133186389efaf243
- https://github.com/thi-ng/umbrella/blob/develop/packages/egf/CHANGELOG.md#040-2021-03-27
- https://www.npmjs.com/package/@thi.ng/egf
