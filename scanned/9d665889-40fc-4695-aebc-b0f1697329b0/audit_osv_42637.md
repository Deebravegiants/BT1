# [M] Cross-Site Request Forgery in the Administrative User Deletion Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-69082
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:L/SI:L/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69082
Type: osv

## Details
CTI-Transmute contained a cross-site request forgery vulnerability in the administrative user deletion functionality. The /account/delete/<id> endpoint accepted HTTP GET requests for an operation that modified application state.

An unauthenticated remote attacker could construct a malicious link or embed a request targeting this endpoint and induce an authenticated CTI-Transmute administrator to visit the attacker-controlled content. If the administrator had an active session, the browser would automatically include the administrator’s session credentials, causing the selected user account to be deleted without the administrator intentionally confirming the operation.

Successful exploitation requires interaction from a currently authenticated administrator who has permission to delete users. The attacker does not need a CTI-Transmute account or administrative privileges because the forged request executes using the victim administrator’s session.

The vulnerability could allow an attacker to delete arbitrary user accounts, resulting in unauthorized modification of application state and denial of access for affected users. Depending on whether administrators can delete other administrators or the final administrative account, exploitation could also disrupt administration of the CTI-Transmute instance.

The patch resolves the issue by restricting the deletion endpoint to HTTP POST requests and submitting the deletion through a form containing a CSRF token.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69082.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69082
- https://github.com/MISP/cti-transmute/commit/4f0d051ec5f1d45894c26987d409411728b2d82c
- https://github.com/MISP/cti-transmute
