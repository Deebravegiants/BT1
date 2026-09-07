# [H] nanoid: custom generators can loop indefinitely when size is zero

## Summary
Severity: High
Advisory: GHSA-2v37-7h3g-55p8
CVE: CVE-2026-67213
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-2v37-7h3g-55p8
Type: github-advisory

## Affected
- npm: `nanoid` — affected >=0 <3.3.18
- npm: `nanoid` — affected >=4.0.0 <5.1.6

## Details
nanoid (Nano ID) before 5.1.6 contains an infinite loop in the customAlphabet and customRandom functions. When these functions are configured with a size of 0, the internal generation loop never satisfies its exit condition and spins indefinitely, hanging the calling thread. An application that passes an unvalidated, attacker-controlled size of 0 to these functions is exposed to a denial-of-service condition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-67213
- https://github.com/ai/nanoid/commit/cb3626d0f3342fdf179cd425fd9c4fbb92c7d0e7
- https://github.com/ai/nanoid/commit/e10f8d40ce9d1ab47f66d65a16b48086432730d0
- https://github.com/ai/nanoid/commit/f9d13f150847d117877adee3460a46eceb0cf49b
- https://github.com/ai/nanoid
- https://github.com/ai/nanoid/releases/tag/3.3.17
- https://github.com/ai/nanoid/releases/tag/3.3.18
- https://github.com/ai/nanoid/releases/tag/5.1.6
- https://www.vulncheck.com/advisories/nanoid-before-infinite-loop-via-zero-size-in-customalphabet-and-customrandom
