# [M] CometVisu Backend for openHAB has a sensitive information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3g4c-hjhr-73rj
CVE: CVE-2024-42470
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-09
Source: https://github.com/advisories/GHSA-3g4c-hjhr-73rj
Type: github-advisory

## Affected
- Maven: `org.openhab.ui.bundles:org.openhab.ui.cometvisu` — affected >=0 <4.2.1

## Details
Several endpoints in the CometVisu add-on of openHAB don't require authentication. This makes it possible for unauthenticated attackers to modify or to steal sensitive data.

## Impact

This issue may lead to sensitive Information Disclosure.

## References
- https://github.com/openhab/openhab-webui/security/advisories/GHSA-3g4c-hjhr-73rj
- https://nvd.nist.gov/vuln/detail/CVE-2024-42470
- https://github.com/openhab/openhab-webui/commit/630e8525835c698cf58856aa43782d92b18087f2
- https://github.com/openhab/openhab-webui
