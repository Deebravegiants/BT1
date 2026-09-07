# [M] eZ Platform Admin UI vulnerable to DOM-based Cross-site Scripting in file upload widget

## Summary
Severity: Medium
Advisory: GHSA-gc5h-6jx9-q2qh
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-gc5h-6jx9-q2qh
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-admin-ui` — affected >=3.3.0 <3.3.39

## Details
### Impact
The file upload widget is vulnerable to XSS payloads in filenames. Access permission to upload files is required. As such, in most cases only authenticated editors and administrators will have the required permission. It is not persistent, i.e. the payload is only executed during the upload. In effect, an attacker will have to trick an editor/administrator into uploading a strangely named file. The fix ensures XSS is escaped.

### Patches
See "Patched versions". Commit: https://github.com/ezsystems/ezplatform-admin-ui/commit/7a9f991b200fa5a03d49cd07f50577c8bc90a30b

### Workarounds
None.

### References
- https://developers.ibexa.co/security-advisories/ibexa-sa-2024-004-dom-based-xss-in-file-upload
- https://github.com/ezsystems/ezplatform-admin-ui/commit/7a9f991b200fa5a03d49cd07f50577c8bc90a30b
- https://github.com/ibexa/admin-ui/security/advisories/GHSA-qm44-wjm2-pr59

### Credit
This vulnerability was discovered and reported to Ibexa by Alec Romano: https://github.com/4rdr
We thank them for reporting it responsibly to us.

How to report security issues:
https://doc.ibexa.co/en/latest/infrastructure_and_maintenance/security/reporting_issues/

## References
- https://github.com/ezsystems/ezplatform-admin-ui/security/advisories/GHSA-gc5h-6jx9-q2qh
- https://github.com/ibexa/admin-ui/security/advisories/GHSA-qm44-wjm2-pr59
- https://github.com/ezsystems/ezplatform-admin-ui/commit/7a9f991b200fa5a03d49cd07f50577c8bc90a30b
- https://developers.ibexa.co/security-advisories/ibexa-sa-2024-004-dom-based-xss-in-file-upload
- https://github.com/ezsystems/ezplatform-admin-ui
