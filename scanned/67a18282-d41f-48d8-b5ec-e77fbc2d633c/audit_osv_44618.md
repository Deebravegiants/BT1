# [H] undici vulnerable to cross-origin cache poisoning via missing origin isolation in interceptors

## Summary
Severity: High
Advisory: CVE-2026-85152
Aliases: GHSA-vp8m-p9jh-q5pm
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85152
Type: osv

## Details
undici 8.10.0 omits the destination origin from the cache and request-deduplication keys when the cache or deduplicate interceptor is composed directly onto a Client or Pool. Because the internal cache key falls back to an empty origin string, a cacheable or in-flight response from one upstream origin is returned for a request to a different, trusted origin whenever the method, path, and relevant headers match, which permits cross-origin information disclosure and persistent cache poisoning. The reporter demonstrated a full authentication bypass in which a JWT signed with an attacker-controlled key was accepted as belonging to a trusted issuer, and the trusted origin was never contacted. This is a regression introduced in 8.10.0 and affects undici versions from 8.10.0 up to 8.10.2. Applications using an Agent, which carries the origin in its dispatch options, are not affected. Users should upgrade to undici 8.10.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85152.json
- https://github.com/nodejs/undici/security/advisories/GHSA-vp8m-p9jh-q5pm
- https://nvd.nist.gov/vuln/detail/CVE-2026-85152
