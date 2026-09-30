# [M] CVE-2025-14714

## Summary
Severity: Medium
Advisory: CVE-2025-14714
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-14714
Type: osv

## Details
An Authentication Bypass vulnerability existed where the application bundled an interpreter (Python) that inherits the Transparency, Consent, and Control (TCC) permissions granted by the user to the main application bundle




By executing the bundled interpreter directly the attacker's scripts run with the application's TCC privileges




In fixed versions parent-constraints are used to allow only the main application to launch interpreter with those permissions

This issue affects LibreOffice on macOS: from 25.2 before < 25.2.4.

## References
- https://www.libreoffice.org/about-us/security/advisories/cve-2025-14714
