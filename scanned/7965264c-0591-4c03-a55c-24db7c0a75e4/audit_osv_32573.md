# [C] NetAlertX Vulnerable to Authentication Bypass

## Summary
Severity: Critical
Advisory: CVE-2025-32440
Aliases: GHSA-h4x5-vr54-vjrx
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-32440
Type: osv

## Details
NetAlertX is a network, presence scanner and alert framework. Prior to version 25.4.14, it is possible to bypass the authentication mechanism of NetAlertX to update settings without authentication. An attacker can trigger sensitive functions within util.php by sending crafted requests to /index.php. This issue has been patched in version 25.4.14.

## References
- https://github.com/jokob-sk/NetAlertX/releases/tag/v25.4.14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32440.json
- https://github.com/jokob-sk/NetAlertX/security/advisories/GHSA-h4x5-vr54-vjrx
- https://nvd.nist.gov/vuln/detail/CVE-2025-32440
