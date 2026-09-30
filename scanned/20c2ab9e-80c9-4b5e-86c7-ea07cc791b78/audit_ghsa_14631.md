# [H] league/commonmark's quadratic complexity bugs may lead to a denial of service

## Summary
Severity: High
Advisory: GHSA-c2pc-g5qf-rfrf
CWE: CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-c2pc-g5qf-rfrf
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=0 <2.6.0

## Details
### Impact

Several polynomial time complexity issues in league/commonmark may lead to unbounded resource exhaustion and subsequent denial of service.

Malicious users could trigger that inefficient code with carefully crafted Markdown inputs that are specifically designed to ensure the worst-case performance is reached.  Sending multiple such requests in parallel could tie up all available CPU resources and/or PHP-FPM processes, leading to denial of service for legitimate users.

### Patches

These vulnerabilities have been patched in version 2.6.0.  All users on older versions are highly encouraged to upgrade as soon as possible.

### Workarounds

If you cannot upgrade, you may be able to mitigate the issues by:

- Setting very low `memory_limit` and `max_execution_time` PHP configurations to prevent runaway resource usage
- Implementing rate-limiting, bot protection, or other approaches to reduce the risk of simultaneous bad requests hitting your site
- Limiting the size of inputs fed into this library (specifically the max length of each line)
- Limiting the use of this library to trusted users

### References

Most of these issues were discovered in other Markdown parsers. You can read more about them here:

* https://github.com/commonmark/commonmark.js/issues/129
* https://github.com/commonmark/commonmark.js/issues/157
* https://github.com/commonmark/commonmark.js/issues/172
* https://github.com/github/cmark-gfm/security/advisories/GHSA-r572-jvj2-3m8p
* https://github.com/github/cmark-gfm/security/advisories/GHSA-24f7-9frr-5h2r
* https://github.com/github/cmark-gfm/security/advisories/GHSA-29g3-96g3-jg6c
* https://github.com/github/cmark-gfm/security/advisories/GHSA-r8vr-c48j-fcc5
* https://github.com/github/cmark-gfm/security/advisories/GHSA-w4qg-3vf7-m9x5
* https://github.com/github/cmark-gfm/security/advisories/GHSA-66g8-4hjf-77xh

For general information about this type of issue:

* https://en.wikipedia.org/wiki/Time_complexity
* https://cwe.mitre.org/data/definitions/407.html

## References
- https://github.com/github/cmark-gfm/security/advisories/GHSA-24f7-9frr-5h2r
- https://github.com/github/cmark-gfm/security/advisories/GHSA-29g3-96g3-jg6c
- https://github.com/github/cmark-gfm/security/advisories/GHSA-66g8-4hjf-77xh
- https://github.com/github/cmark-gfm/security/advisories/GHSA-r572-jvj2-3m8p
- https://github.com/github/cmark-gfm/security/advisories/GHSA-r8vr-c48j-fcc5
- https://github.com/github/cmark-gfm/security/advisories/GHSA-w4qg-3vf7-m9x5
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-c2pc-g5qf-rfrf
- https://github.com/commonmark/commonmark.js/issues/129
- https://github.com/commonmark/commonmark.js/issues/157
- https://github.com/commonmark/commonmark.js/issues/172
- https://github.com/thephpleague/commonmark
