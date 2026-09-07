# [M] Kimai: Login CSRF in the Timesheet Stop and Restart API Endpoints Allows Unauthorized State Changes

## Summary
Severity: Medium
Advisory: GHSA-r8vr-m544-qh4h
CVE: CVE-2026-52823
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-r8vr-m544-qh4h
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.58.0

## Details
### Summary

Kimai 2.56.0 contains authenticated cross-site request forgery issues in its timesheet state-changing API endpoints. The application reuses the browser's existing session for `/api/*` requests, and both the `stop` and `restart` operations are exposed through `GET` and `PATCH` routes that directly modify business state.

As a result, an attacker can trick a logged-in user into visiting a malicious page and cause unauthorized timesheet actions without the victim's consent. Depending on the endpoint, this can stop a running timesheet or create and start a new one from historical data.

### Details

The issue affects at least the following API routes:

- `GET /api/timesheets/{id}/stop`
- `GET /api/timesheets/{id}/restart`

Both routes are non-read-only operations but are still exposed as `GET`. In `src/API/TimesheetController.php`.

*A PoC was provided, but removed for security reasons.*

### Impact

This vulnerability allows an attacker to trigger unauthorized business-state changes as a logged-in victim. In the validated `stop` case, a running timesheet can be stopped, affecting time tracking integrity and potentially availability of ongoing work tracking. In the `restart` case, a historical timesheet can be restarted and a new record can be created without the victim's knowledge.

These actions can corrupt time records, distort billing and reporting, interfere with approvals or audits, and create persistent database-side side effects. Because exploitation requires only that the victim visit a malicious page while authenticated, the attack barrier is low.

# Solution

The `GET` routes were removed, both `stop` and `restart` are only available via `PATCH`.

See [https://www.kimai.org/en/security/ghsa-r8vr-m544-qh4h](https://www.kimai.org/en/security/ghsa-r8vr-m544-qh4h) for more information.

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-r8vr-m544-qh4h
- https://github.com/kimai/kimai
