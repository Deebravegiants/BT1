# [H] ChurchCRM: Cross-Site Request Forgery (CSRF) in SelectDelete.php Leading to Permanent Data Deletion

## Summary
Severity: High
Advisory: CVE-2026-40581
Aliases: GHSA-6qxv-xw9j-77pj
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40581
Type: osv

## Details
ChurchCRM is an open-source church management system. In versions prior to 7.2.0, the family record deletion endpoint (SelectDelete.php) performs permanent, irreversible deletion of family records and all associated data via a plain GET request with no CSRF token validation. An attacker can craft a malicious page that, when visited by an authenticated administrator, silently triggers deletion of targeted family records including associated notes, pledges, persons, and property data without any user interaction. This issue has been fixed in version 7.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40581.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-6qxv-xw9j-77pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-40581
- https://github.com/ChurchCRM/CRM/commit/39361628613af7682b813f3e62a412559616d674
- https://github.com/ChurchCRM/CRM/pull/8613
