# [H] find-my-way has a ReDoS vulnerability in multiparametric routes

## Summary
Severity: High
Advisory: GHSA-rrr8-f88r-h8q6
CVE: CVE-2024-45813
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-rrr8-f88r-h8q6
Type: github-advisory

## Affected
- npm: `find-my-way` — affected >=5.5.0 <8.2.2
- npm: `find-my-way` — affected >=9.0.0 <9.0.1

## Details
### Impact

A bad regular expression is generated any time you have two parameters within a single segment, when adding a `-` at the end, like `/:a-:b-`.

### Patches

Update to find-my-way v8.2.2 or v9.0.1. or subsequent versions.

### Workarounds

No known workarounds.

### References

- [CVE-2024-45296](https://github.com/advisories/GHSA-9wv6-86v2-598j)
- [Detailed blog post about `path-to-regexp` vulnerability](https://blakeembrey.com/posts/2024-09-web-redos/)

## References
- https://github.com/delvedor/find-my-way/security/advisories/GHSA-rrr8-f88r-h8q6
- https://nvd.nist.gov/vuln/detail/CVE-2024-45813
- https://github.com/delvedor/find-my-way/commit/17fae694dcefc056045da201681c1530f0f80518
- https://github.com/delvedor/find-my-way/commit/5e9e0eb5d8d438e06a185d5e536a896572dd0440
- https://github.com/delvedor/find-my-way/commit/66fa03923355b8da1db4ba572d66a4fee4a57cf5
- https://blakeembrey.com/posts/2024-09-web-redos
- https://github.com/advisories/GHSA-9wv6-86v2-598j
- https://github.com/delvedor/find-my-way
