# [H] Parse Server leaks protected fields via LiveQuery afterEvent trigger

## Summary
Severity: High
Advisory: GHSA-5hmj-jcgp-6hff
CVE: CVE-2026-33163
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-5hmj-jcgp-6hff
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.35
- npm: `parse-server` — affected >=0 <8.6.50

## Details
### Impact

When a `Parse.Cloud.afterLiveQueryEvent` trigger is registered for a class, the LiveQuery server leaks protected fields and `authData` to all subscribers of that class. Fields configured as protected via Class-Level Permissions (`protectedFields`) are included in LiveQuery event payloads for all event types (create, update, delete, enter, leave).

Any user with sufficient CLP permissions to subscribe to the affected class can receive protected field data of other users, including sensitive personal information and OAuth tokens from third-party authentication providers.

### Patches

The vulnerability was caused by a reference detachment bug. When an `afterEvent` trigger is registered, the LiveQuery server converts the event object to a `Parse.Object` for the trigger, then creates a new JSON copy via `toJSONwithObjects()`. The sensitive data filter was applied to the `Parse.Object` reference, but the unfiltered JSON copy was sent to clients. The fix ensures that the JSON copy is assigned back to the response object before filtering, so the filter operates on the actual data sent to clients.

### Workarounds

Remove all `Parse.Cloud.afterLiveQueryEvent` trigger registrations. Without an `afterEvent` trigger, the reference detachment does not occur and protected fields are correctly filtered.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-5hmj-jcgp-6hff
- https://nvd.nist.gov/vuln/detail/CVE-2026-33163
- https://github.com/parse-community/parse-server/pull/10232
- https://github.com/parse-community/parse-server/pull/10233
- https://github.com/parse-community/parse-server
