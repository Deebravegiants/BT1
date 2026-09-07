# [M] Cockpit - Content Platform vulnerable to XSS through name or email argument names

## Summary
Severity: Medium
Advisory: GHSA-j4rj-fgcq-wmqp
CVE: CVE-2025-7053
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-07-04
Source: https://github.com/advisories/GHSA-j4rj-fgcq-wmqp
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.11.4

## Details
A vulnerability was found in Cockpit versions up to 2.11.3. This issue affects some unknown processing instances of the file /system/users/save. The manipulation of the arguments "name" or "email" leads to cross-site scripting. The attack may be initiated remotely. Upgrading to version 2.11.4 will address this issue. It is recommended to upgrade the affected component. The vendor was contacted early about this disclosure and acted accordingly. A patch and new release were made available very quickly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7053
- https://github.com/Cockpit-HQ/Cockpit/commit/bdcd5e3bc651c0839c7eea807f3eb6af856dbc76
- https://github.com/Cockpit-HQ/Cockpit
- https://github.com/Cockpit-HQ/Cockpit/releases/tag/2.11.4
- https://vuldb.com/?ctiid.314819
- https://vuldb.com/?id.314819
- https://vuldb.com/?submit.605594
