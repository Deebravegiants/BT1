# [H] fast-uri vulnerable to host confusion via percent-encoded authority delimiters

## Summary
Severity: High
Advisory: GHSA-v39h-62p7-jpjc
CVE: CVE-2026-6322
CWE: CWE-140, CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-v39h-62p7-jpjc
Type: github-advisory

## Affected
- npm: `fast-uri` — affected >=3.0.0 <3.1.2
- npm: `fast-uri` — affected >=0 <2.4.1

## Details
### Impact

`fast-uri` v3.1.1 and earlier decodes percent-encoded authority delimiters (`%40` as `@`, `%3A` as `:`) inside the host component and serializes them back as raw characters. This changes the URI structure, turning a hostname into userinfo plus a different host.

For example, `http://trusted.com%40evil.com/` normalizes to `http://trusted.com@evil.com/`, which reparses as host `evil.com` with userinfo `trusted.com`.

Applications that normalize untrusted URLs before host allowlist checks, redirect validation, or outbound request routing can be steered to a different authority than the original URL appeared to contain.

### Patches

Upgrade to `fast-uri` >= 3.1.2, or if you are in the v2.x release line, v2.4.1

### Workarounds

None. Upgrade to the patched version.

## References
- https://github.com/fastify/fast-uri/security/advisories/GHSA-v39h-62p7-jpjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-6322
- https://access.redhat.com/errata/RHSA-2026:41928
- https://access.redhat.com/errata/RHSA-2026:41951
- https://access.redhat.com/errata/RHSA-2026:42078
- https://access.redhat.com/errata/RHSA-2026:42142
- https://access.redhat.com/errata/RHSA-2026:43038
- https://access.redhat.com/errata/RHSA-2026:54395
- https://access.redhat.com/errata/RHSA-2026:54555
- https://access.redhat.com/errata/RHSA-2026:56366
- https://access.redhat.com/errata/RHSA-2026:56431
- https://access.redhat.com/errata/RHSA-2026:56928
- https://access.redhat.com/errata/RHSA-2026:56968
- https://access.redhat.com/errata/RHSA-2026:57013
- https://access.redhat.com/errata/RHSA-2026:57487
- https://access.redhat.com/errata/RHSA-2026:60520
- https://access.redhat.com/errata/RHSA-2026:60855
- https://access.redhat.com/errata/RHSA-2026:61783
- https://access.redhat.com/security/cve/CVE-2026-6322
- https://bugzilla.redhat.com/show_bug.cgi?id=2466684
