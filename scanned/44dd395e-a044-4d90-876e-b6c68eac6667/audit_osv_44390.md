# [H] Flowintel Fails to Invalidate Active Sessions After Password Change

## Summary
Severity: High
Advisory: CVE-2026-81826
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81826
Type: osv

## Details
Affected versions of Flowintel do not revoke existing authenticated sessions when a user’s password is changed.


This means that if an attacker already possesses a valid session—for example, from prior access or a stolen session token—the victim changing their password does not terminate that attacker’s access. The session remains usable until it expires naturally. The upstream commit describes this directly as:


“session keeps working until it expires.”

The fix detects password changes and explicitly invokes _invalidate_user_sessions(user.id) after the database update. This is applied in both edit_user_core() and admin_edit_user_core().

Version impacted >=3.3.0

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81826.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81826
- https://github.com/flowintel/flowintel/commit/e46e075b8f28212800fc57ead0a7f9a2921bfff0.patch
- https://github.com/flowintel/flowintel
