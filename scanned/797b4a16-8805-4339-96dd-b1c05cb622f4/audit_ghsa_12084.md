# [H] LiveQuery protected field leak via shared mutable state across concurrent subscribers

## Summary
Severity: High
Advisory: GHSA-m983-v2ff-wq65
CVE: CVE-2026-34363
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-m983-v2ff-wq65
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.7.0-alpha.9
- npm: `parse-server` — affected >=0 <8.6.65

## Details
### Impact

When multiple clients subscribe to the same class via LiveQuery, the event handlers process each subscriber concurrently using shared mutable objects. The sensitive data filter modifies these shared objects in-place, so when one subscriber's filter removes a protected field, subsequent subscribers may receive the already-filtered object. This can cause protected fields and authentication data to leak to clients that should not see them, or cause clients that should see the data to receive an incomplete object.

Additionally, when an afterEvent Cloud Code trigger is registered, one subscriber's trigger modifications can leak to other subscribers through the same shared mutable state.

Any Parse Server deployment using LiveQuery with protected fields or afterEvent triggers is affected when multiple clients subscribe to the same class.

### Patches

The fix deep-clones the shared objects at the start of each subscriber's processing callback, ensuring each subscriber works on an independent copy. Additionally, a bug was fixed where master key LiveQuery clients could not receive events on classes with protected fields due to an incorrect type passed to the sensitive data filter.

### Workarounds

There is no known workaround.

### Resources

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-m983-v2ff-wq65
- Fix Parse Server 9: https://github.com/parse-community/parse-server/pull/10330
- Fix Parse Server 8: https://github.com/parse-community/parse-server/pull/10331

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-m983-v2ff-wq65
- https://nvd.nist.gov/vuln/detail/CVE-2026-34363
- https://github.com/parse-community/parse-server/pull/10330
- https://github.com/parse-community/parse-server/pull/10331
- https://github.com/parse-community/parse-server/commit/5834e29234593addaa0251a85f572ad4f376320b
- https://github.com/parse-community/parse-server/commit/776c71c3078e77d38c94937f463741793609d055
- https://github.com/parse-community/parse-server
