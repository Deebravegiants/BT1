# [M] Kimai 2 vulnerable to persistent cross-site scripting in the timesheet descriptions

## Summary
Severity: Medium
Advisory: GHSA-9278-6hcj-2p4j
CVE: CVE-2019-25317
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-9278-6hcj-2p4j
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <1.1

## Details
Kimai 2 contains a persistent cross-site scripting vulnerability that allows attackers to inject malicious scripts into timesheet descriptions. Attackers can insert SVG-based XSS payloads in the description field to execute arbitrary JavaScript when the page is loaded and viewed by other users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25317
- https://github.com/kevinpapst/kimai2/pull/962
- https://github.com/kimai/kimai/commit/a0e8aa3a435717187fb12210242dab1b7c97ff3f
- https://github.com/kevinpapst/kimai2
- https://github.com/kimai/kimai
- https://www.exploit-db.com/exploits/47286
- https://www.vulncheck.com/advisories/kimai-persistent-cross-site-scripting-xss
