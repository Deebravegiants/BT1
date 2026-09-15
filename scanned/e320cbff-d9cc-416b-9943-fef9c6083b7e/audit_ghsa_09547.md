# [H] fast-uri vulnerable to path traversal via percent-encoded dot segments

## Summary
Severity: High
Advisory: GHSA-q3j6-qgpj-74h6
CVE: CVE-2026-6321
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-q3j6-qgpj-74h6
Type: github-advisory

## Affected
- npm: `fast-uri` — affected >=3.0.0 <3.1.1
- npm: `fast-uri` — affected >=0 <2.4.1

## Details
### Impact

`fast-uri` v3.1.0 and earlier decodes percent-encoded path separators (`%2F`) and dot segments (`%2E`) before applying dot-segment removal in `normalize()` and `equal()`. This makes encoded path data behave like real `/` and `..`, so distinct URIs collapse onto the same normalized path.

For example, `http://example.com/public/%2e%2e/admin` normalizes to `http://example.com/admin`, and `equal()` considers them the same URI.

Applications that normalize or compare attacker-controlled URLs to enforce path-based policy can be bypassed. A path that looks confined under an allowed prefix can normalize to a different location.

### Patches

Upgrade to `fast-uri` >= 3.1.1, or if you are in the v2.x release line, v2.4.1

### Workarounds

None. Upgrade to the patched version.

## References
- https://github.com/fastify/fast-uri/security/advisories/GHSA-q3j6-qgpj-74h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-6321
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-6321.json
- https://github.com/fastify/fast-uri/releases/tag/v3.1.1
- https://github.com/fastify/fast-uri/releases/tag/v2.4.1
- https://github.com/fastify/fast-uri
- https://cna.openjsf.org/security-advisories.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2466582
- https://access.redhat.com/security/cve/CVE-2026-6321
- https://access.redhat.com/errata/RHSA-2026:57013
- https://access.redhat.com/errata/RHSA-2026:56928
- https://access.redhat.com/errata/RHSA-2026:56431
- https://access.redhat.com/errata/RHSA-2026:56366
- https://access.redhat.com/errata/RHSA-2026:42079
- https://access.redhat.com/errata/RHSA-2026:42078
- https://access.redhat.com/errata/RHSA-2026:37385
- https://access.redhat.com/errata/RHSA-2026:34342
- https://access.redhat.com/errata/RHSA-2026:26420
- https://access.redhat.com/errata/RHSA-2026:26416
- https://access.redhat.com/errata/RHSA-2026:26234
