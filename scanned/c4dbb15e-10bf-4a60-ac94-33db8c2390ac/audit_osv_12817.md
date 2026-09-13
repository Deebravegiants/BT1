# [C] CVE-2018-15152

## Summary
Severity: Critical
Advisory: CVE-2018-15152
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-08-15
Source: https://osv.dev/vulnerability/CVE-2018-15152
Type: osv

## Details
Authentication bypass vulnerability in portal/account/register.php in versions of OpenEMR before 5.0.1.4 allows a remote attacker to access (1) portal/add_edit_event_user.php, (2) portal/find_appt_popup_user.php, (3) portal/get_allergies.php, (4) portal/get_amendments.php, (5) portal/get_lab_results.php, (6) portal/get_medications.php, (7) portal/get_patient_documents.php, (8) portal/get_problems.php, (9) portal/get_profile.php, (10) portal/portal_payment.php, (11) portal/messaging/messages.php, (12) portal/messaging/secure_chat.php, (13) portal/report/pat_ledger.php, (14) portal/report/portal_custom_report.php, or (15) portal/report/portal_patient_report.php without authenticating as a patient.

## References
- https://insecurity.sh/reports/openemr.pdf
- https://github.com/openemr/openemr/pull/1758/files
- https://www.open-emr.org/wiki/index.php/OpenEMR_Patches
- http://packetstormsecurity.com/files/163181/OpenEMR-5.0.1.3-Authentication-Bypass.html
- https://github.com/Hacker5preme/Exploits/tree/main/CVE-2018-15152-Exploit
- https://www.databreaches.net/openemr-patches-serious-vulnerabilities-uncovered-by-project-insecurity/
