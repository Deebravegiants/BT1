# [H] OpenEMR's Portal Payment Endpoint Trusts User-Controlled pid

## Summary
Severity: High
Advisory: CVE-2026-25147
Aliases: GHSA-mwmw-qxv3-8whh
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-25147
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, in `portal/portal_payment.php`, the patient id used for the page is taken from the request (`$pid = $_REQUEST['pid'] ?? $pid` and `$pid = ($_REQUEST['hidden_patient_code'] ?? null) > 0 ? $_REQUEST['hidden_patient_code'] : $pid`) instead of being fixed to the authenticated portal user. The portal session already has a valid `$pid` for the logged-in patient. Overwriting it with user-supplied values and using it without authorization allows a portal user to view and interact with another patient's demographics, invoices, and payment history—horizontal privilege escalation and IDOR. Version 8.0.0 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25147.json
- https://github.com/openemr/openemr/security/advisories/GHSA-mwmw-qxv3-8whh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25147
- https://github.com/openemr/openemr/commit/d6ab3cd0b621b19b942cf49d2db2026e288aa214
