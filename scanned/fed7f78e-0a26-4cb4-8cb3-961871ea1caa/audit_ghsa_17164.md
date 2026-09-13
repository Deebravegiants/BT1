# [M] RaspAP Vulnerable to Code Injection via an Unknown Process in File `includes/provider.php`

## Summary
Severity: Medium
Advisory: GHSA-99wg-vmvq-2cp5
CVE: CVE-2024-2497
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-99wg-vmvq-2cp5
Type: github-advisory

## Affected
- Packagist: `billz/raspap-webgui` — affected >=0

## Details
A vulnerability was found in RaspAP raspap-webgui 3.0.9 and classified as critical. This issue affects some unknown processing of the file includes/provider.php of the component HTTP POST Request Handler. The manipulation of the argument country leads to code injection. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-256919. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2497
- https://github.com/RaspAP/raspap-webgui
- https://toradah.notion.site/Code-Injection-Leading-to-Remote-Code-Execution-RCE-in-RaspAP-Web-GUI-d321e1a416694520bec7099253c65060?pvs=4
- https://vuldb.com/?ctiid.256919
- https://vuldb.com/?id.256919
