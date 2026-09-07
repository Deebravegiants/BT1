# [H] Angular's deprecated package has a Cross-Site Scripting issue

## Summary
Severity: High
Advisory: GHSA-7x27-g8rg-x87w
CVE: CVE-2026-11998
CWE: CWE-79, CWE-791
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-24
Source: https://github.com/advisories/GHSA-7x27-g8rg-x87w
Type: github-advisory

## Affected
- npm: `angular` — affected >=1.2.0-rc.3

## Details
A flaw in AngularJS' Strict Contextual Escaping (SCE) logic allows bypassing certain SCE policies for resource URLs and can lead to arbitrary JavaScript execution within the context of the victim's browser session.


SCE's purpose is to ensure that only trusted or safe values are used in certain security-sensitive contexts, such as resource URLs, including URLs that define executable JavaScript scripts, '<iframe>' documents, route templates, etc. A flaw in the logic that tries to match entire URLs against regular expression matchers can result in partial matches for certain types of regular expressions, effectively bypassing the policies and allowing the use of unsafe values as resource URLs.


This issue affects AngularJS versions greater than or equal to 1.2.0-rc.3.


Note:
The AngularJS project was already End-of-Life when this CVE was published and will not receive any updates to address this issue. For more information see the  End-of-Life announcement https://docs.angularjs.org/misc/version-support-status .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11998
- https://access.redhat.com/security/cve/CVE-2026-11998
- https://bugzilla.redhat.com/show_bug.cgi?id=2492579
- https://codepen.io/herodevs/pen/JobQdmz/5b3896f56fab66f20cd25e698cf3faa8
- https://github.com/angular/angular.js
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-11998.json
- https://www.herodevs.com/vulnerability-directory/cve-2026-11998
- https://www.herodevs.com/vulnerability-directory/cve-2026-11998?nes-for-angularjs
