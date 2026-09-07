# [H] Concrete CMS is vulnerable to PHP Object Injection via unserialize() calls in the Workflow, Form block, and File/Set components

## Summary
Severity: High
Advisory: GHSA-52pr-7vmf-2w7x
CVE: CVE-2026-7888
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-52pr-7vmf-2w7x
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.2

## Details
Concrete CMS below 9.5.2 is vulnerable to PHP Object Injection via unserialize() calls in the Workflow, Form block, and File/Set components that lack the allowed_classes restriction. An unauthenticated attacker may trigger arbitrary PHP object instantiation if a malicious serialized payload has been placed in the database. The Concrete CMS security team thanks XananasX7 and Sanjorn Keeratirungsan (dizconnect) for both independently reporting this ssue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7888
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/952-release-notes
- https://github.com/concretecms/concretecms
- https://github.com/concretecms/concretecms/releases/tag/9.5.2
