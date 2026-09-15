# [M] Poweradmin: CSV Injection in log export endpoints allows formula execution in spreadsheet applications

## Summary
Severity: Medium
Advisory: GHSA-3h6h-67x3-cv5x
CVE: CVE-2026-47693
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-3h6h-67x3-cv5x
Type: github-advisory

## Affected
- Packagist: `poweradmin/poweradmin` — affected >=0 <4.2.4
- Packagist: `poweradmin/poweradmin` — affected >=4.3.0 <4.3.3

## Details
Description:

### Summary

Poweradmin v4.4.0 is vulnerable to CSV Injection (Formula Injection) in its log export functionality. User-controlled data — specifically the username field — is written to exported CSV files without sanitizing formula trigger characters (=, +, -, @). When an administrator exports activity logs and opens the resulting CSV in a spreadsheet application (Microsoft Excel, LibreOffice Calc, Google Sheets), any formula stored in a username is executed by the application. This can be used for phishing attacks against administrators or data exfiltration.

### Details

The vulnerability exists in all four log export controllers:

- `lib/Application/Controller/ListLogUsersController.php` (lines 188, 194)
- `lib/Application/Controller/ListLogZonesController.php`
- `lib/Application/Controller/ListLogGroupsController.php`
- `lib/Application/Controller/ListLogApiController.php`

These controllers export database rows via `fputcsv()` without applying any formula injection countermeasures. The `user` column contains the username of the actor who performed the operation, and the `username` column (in user logs) contains the username of the affected account. Both fields are written verbatim to the CSV output.

A username such as `=1+1` is written **without CSV enclosure quotes** (because it contains no commas or quotes), so spreadsheet applications treat it directly as a formula. A username containing commas or quotes (e.g. `=HYPERLINK("http://attacker.com","Click here")`) is enclosed in CSV quotes with internal quotes doubled, but spreadsheet applications still evaluate the cell value as a formula since it begins with `=`.

Additionally, PHP deprecation warnings are emitted directly into the HTTP response body before CSV headers, exposing internal file paths (e.g. `/app/lib/Application/Controller/ListLogUsersController.php`) — a secondary information disclosure issue (CWE-209). This also corrupts the CSV file when PHP error reporting is enabled.

### PoC

**Prerequisites:** An account with `user_add_new` permission (administrator role).

**Steps to reproduce:**

1. Log in as administrator.
2. Navigate to Add User and create an account with:
   - Username: `=HYPERLINK("http://attacker.com","Confirm Identity")`
   - Any valid email and password
3. Log out, then log in with the newly created account to generate a log entry.
4. Log back in as administrator.
5. Navigate to `/users/logs` and click Export CSV.
6. Open the downloaded CSV file in Microsoft Excel or LibreOffice Calc.

**Result:** Excel renders a clickable hyperlink labeled "Confirm Identity" pointing to `http://attacker.com` in the `user` column of the log entry. With the simpler username `=1+1`, the cell displays `2` instead of the literal text, confirming formula execution.

Confirmed on Poweradmin v4.4.0 (Docker image `poweradmin/poweradmin:latest`).

### Impact

This is a CSV Injection vulnerability (CWE-1236). It affects any administrator who exports activity logs to CSV and opens the file in a spreadsheet application.

**Attack scenarios:**

- **Phishing:** A malicious actor with the ability to create user accounts sets a formula username that renders as a convincing link in the exported report, tricking a higher-privileged administrator into clicking it.
- **Data exfiltration:** Using `=IMPORTXML()` in Google Sheets or similar, adjacent cell data (log contents) can be sent to an attacker-controlled server silently when the sheet is opened.

## References
- https://github.com/poweradmin/poweradmin/security/advisories/GHSA-3h6h-67x3-cv5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-47693
- https://github.com/poweradmin/poweradmin
- https://github.com/poweradmin/poweradmin/releases/tag/v4.2.4
- https://github.com/poweradmin/poweradmin/releases/tag/v4.3.3
