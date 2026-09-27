# [H] Before action, Ash's hooks may execute in certain scenarios despite a request being forbidden

## Summary
Severity: High
Advisory: GHSA-jj4j-x5ww-cwh9
CVE: CVE-2025-48042
CWE: CWE-863
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-jj4j-x5ww-cwh9
Type: github-advisory

## Affected
- Hex: `ash` — affected >=0 <3.5.39

## Details
### Summary
Certain bulk action calls with a `before_transaction` hook and no `after_transaction` hook, will call the `before_transaction` hook before authorization is checked and a Forbidden error is returned, when called as a bulk action.

The impact is that a malicious user could cause a `before_transaction` to run even though they are not authorized to perform the whole action. The `before_action` could run a sensitive/expensive operation.

### Impact
A malicious user could cause a `before_action` to run even though they are not authorized to perform the whole action.

You are affected if you have an create, update or destroy action that:

- has a before_transaction hook on it, and no after_transaction hook on it.
- is being used via an `Ash.bulk_*` callback (which AshJsonApi and AshGraphql do for update/destroy actions)

Whether or not or how much it matters depends on the nature of those before_transaction callbacks. If those before_transaction callbacks are side-effectful, or just doing something like looking up some external data. If your API endpoints are behind authentication and what kind. 

### Severity

The severity for this was hard to gauge. `before_transaction` hooks are not that commonly used. Additionally, any attacker must know which of these things are available to them, be authenticated to make such a request (i.e you very rarely have policies preventing the running of anonymous queries), so privileges and inside knowledge are required. Additionally, the action will always return a `forbidden` error, so no information is revealed. We will evaluate and adjust the severity in the next few days as needed.

It is currently marked as High, given that we really don't know what logic folks are putting in their before_transaction hooks and it could theoretically be very bad.

### Workarounds

You should update ASAP, but if for whatever reason you cannot update, you can add logic to those before_transaction hooks to prevent them from doing their logic before they should.

## References
- https://github.com/ash-project/ash/security/advisories/GHSA-jj4j-x5ww-cwh9
- https://nvd.nist.gov/vuln/detail/CVE-2025-48042
- https://github.com/ash-project/ash/commit/5d1b6a5d00771fd468a509778637527b5218be9a
- https://cna.erlef.org/cves/CVE-2025-48042.html
- https://github.com/ash-project/ash
- https://osv.dev/vulnerability/EEF-CVE-2025-48042
