# [H] @wakaru/cli arbitrary file write during bundle unpack

## Summary
Severity: High
Advisory: GHSA-7wpj-vvmv-pgm8
CVE: CVE-2026-54545
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-7wpj-vvmv-pgm8
Type: github-advisory

## Affected
- npm: `@wakaru/cli` — affected >=1.0.0 <1.4.0

## Details
### Impact

`@wakaru/cli` is vulnerable to arbitrary file write when unpacking a crafted JavaScript bundle with `--unpack`.

Bundle-controlled module filenames were sanitized before writing extracted modules to the output directory. A crafted filename containing overlapping path traversal characters, such as `....//`, could be transformed into `../` after sanitization. This allowed the final output path to escape the intended output directory.

An attacker who can cause a user to run `wakaru --unpack` on a malicious bundle may be able to write files outside the selected output directory. Depending on the target path and user environment, this may lead to code execution.

Affected versions: `>=1.0.0 <1.4.0`.

### Patches

The issue has been patched in `@wakaru/cli@1.4.0`.

Users should upgrade to:

```sh
npm install @wakaru/cli@latest
```

or specifically:
```
npm install @wakaru/cli@1.4.0
```

### Workarounds

Do not run `wakaru --unpack` on untrusted or unknown bundles with affected versions.

If upgrading immediately is not possible, avoid using `--unpack on files that may be attacker-controlled.

## References
- https://github.com/pionxzh/wakaru/security/advisories/GHSA-7wpj-vvmv-pgm8
- https://github.com/pionxzh/wakaru/commit/1d30383b20a6f768786b8ada2f1b0945de13c316
- https://github.com/pionxzh/wakaru
- https://github.com/pionxzh/wakaru/releases/tag/v1.4.0
