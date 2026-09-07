# [M] Parse Server has a protected field change detection oracle via LiveQuery watch parameter

## Summary
Severity: Medium
Advisory: GHSA-qpc3-fg4j-8hgm
CVE: CVE-2026-33429
CWE: CWE-203
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-qpc3-fg4j-8hgm
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.43
- npm: `parse-server` — affected >=0 <8.6.54

## Details
### Impact

An attacker can subscribe to LiveQuery with a `watch` parameter targeting a protected field. Although the protected field value is properly stripped from event payloads, the presence or absence of update events reveals whether the protected field changed, creating a binary oracle. For boolean protected fields, the timing of change events is equivalent to knowing the field value.

### Patches

The `watch` parameter is now validated against protected fields at subscription time, mirroring the existing validation for the `where` clause. Subscriptions that include protected fields in `watch` are rejected with a permission error. Master key connections are exempt.

### Workarounds

None.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-qpc3-fg4j-8hgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33429
- https://github.com/parse-community/parse-server/pull/10253
- https://github.com/parse-community/parse-server/pull/10254
- https://github.com/parse-community/parse-server/commit/0c0a0a5a37ca821d2553119f2cb3be35322eda4b
- https://github.com/parse-community/parse-server/commit/c62eacaf38de86913f09240583448360b1cc8e67
- https://github.com/parse-community/parse-server
