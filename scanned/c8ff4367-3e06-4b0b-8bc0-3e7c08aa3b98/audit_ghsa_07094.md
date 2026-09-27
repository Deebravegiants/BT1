# [H] Prompty: Arbitrary file read via file reference expansion

## Summary
Severity: High
Advisory: GHSA-wxhm-2mq7-7697
CVE: CVE-2026-53598
CWE: CWE-200, CWE-22
Ecosystem: NuGet, PyPI, crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-wxhm-2mq7-7697
Type: github-advisory

## Affected
- PyPI: `prompty` — affected >=0 <2.0.0b2
- npm: `@prompty/core` — affected >=0 <2.0.0-beta.2
- crates.io: `prompty` — affected >=0 <2.0.0-beta.2
- NuGet: `Prompty.Core` — affected >=0 <2.0.0-beta.2

## Details
## Summary
Prompty loaders expanded `${file:...}` references in `.prompty` frontmatter without enforcing that the resolved path stayed within an authorized directory. An attacker-controlled prompt file could use path traversal or an absolute path to cause the host application to read files accessible to the process.

## Affected packages
- PyPI `prompty` versions `<= 2.0.0b1`; fixed in `2.0.0b2`
- npm `@prompty/core` versions `<= 2.0.0-beta.1`; fixed in `2.0.0-beta.2`
- crates.io `prompty` versions `<= 2.0.0-beta.1`; fixed in `2.0.0-beta.2`
- NuGet `Prompty.Core` versions `<= 2.0.0-beta.1`; fixed in `2.0.0-beta.2`

## Impact
Applications that load untrusted `.prompty` files, user-provided prompt paths, or prompt bundles from less-trusted locations could disclose local files available to the application process when expanded values are logged, returned, or otherwise exposed.

## Remediation
Upgrade to the fixed runtime version for your ecosystem. The fix makes file references secure by default: `${file:...}` may only resolve within the directory tree containing the `.prompty` file. Host applications that need shared prompt assets outside that tree must explicitly provide allowed file roots through runtime load options. Absolute paths, `..` traversal, and symlink escapes outside allowed roots are rejected.

## Fix details
The patched runtimes canonicalize file-reference targets and allowed roots before reading referenced files, reject targets outside the prompt directory by default, and add regression coverage for traversal, absolute paths, explicit allowlists, and symlink escapes. The release commit is `88ac9948d7d37995edbb2f6d36913436626c39e1`.

## References
- https://github.com/microsoft/prompty/security/advisories/GHSA-wxhm-2mq7-7697
- https://nvd.nist.gov/vuln/detail/CVE-2026-53598
- https://github.com/microsoft/prompty/commit/88ac9948d7d37995edbb2f6d36913436626c39e1
- https://github.com/microsoft/prompty
