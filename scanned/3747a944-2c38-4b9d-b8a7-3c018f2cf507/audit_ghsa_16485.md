# [M] Pug allows JavaScript code execution if an application accepts untrusted input

## Summary
Severity: Medium
Advisory: GHSA-3965-hpx2-q597
CVE: CVE-2024-36361
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-24
Source: https://github.com/advisories/GHSA-3965-hpx2-q597
Type: github-advisory

## Affected
- npm: `pug-code-gen` — affected >=0 <3.0.3
- npm: `pug` — affected >=0 <3.0.3

## Details
Pug through 3.0.2 allows JavaScript code execution if an application accepts untrusted input for the name option of the `compileClient`, `compileFileClient`, or `compileClientWithDependenciesTracked` function. NOTE: these functions are for compiling Pug templates into JavaScript, and there would typically be no reason to allow untrusted callers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36361
- https://github.com/pugjs/pug/pull/3428
- https://github.com/pugjs/pug/pull/3438
- https://github.com/pugjs/pug/commit/32acfe8f197dc44c54e8af32c7d7b19aa9d350fb
- https://github.com/Coding-Competition-Team/hackac-2024/tree/main/web/pug
- https://github.com/pugjs/pug
- https://github.com/pugjs/pug/blob/4767cafea0af3d3f935553df0f9a8a6e76d470c2/packages/pug/lib/index.js#L328
- https://github.com/pugjs/pug/releases/tag/pug%403.0.3
- https://pugjs.org/api/reference.html
- https://www.npmjs.com/package/pug-code-gen
