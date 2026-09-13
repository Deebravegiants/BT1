# [H] nanoid: non-secure generators can loop indefinitely with negative size

## Summary
Severity: High
Advisory: GHSA-28wg-ghj8-5hjv
CVE: CVE-2026-67214
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-28wg-ghj8-5hjv
Type: github-advisory

## Affected
- npm: `nanoid` — affected >=0 <3.3.16
- npm: `nanoid` — affected >=4.0.0 <5.1.16

## Details
nanoid (Nano ID) before 5.1.16 contains an infinite loop in the customAlphabet and nanoid functions of its non-secure module (nanoid/non-secure). When these functions are given a negative size, the loop counter is decremented from a negative value and never reaches its termination condition, spinning indefinitely and hanging the calling thread. An application that passes an unvalidated, attacker-controlled negative size to these functions is exposed to a denial-of-service condition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-67214
- https://github.com/ai/nanoid/pull/600
- https://github.com/ai/nanoid/pull/601
- https://github.com/ai/nanoid/commit/6ccc67bbaba71d3d77a21d9b636f4171a268ce49
- https://github.com/ai/nanoid/commit/e835c9b71eab832bc6106944bdd26ea96cf2c66d
- https://github.com/ai/nanoid
- https://github.com/ai/nanoid/releases/tag/5.1.16
- https://www.vulncheck.com/advisories/nanoid-before-infinite-loop-via-negative-size-in-non-secure-module
