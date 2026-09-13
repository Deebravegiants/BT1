# [H] Authorization Bypass Through User-Controlled Key in Prospero Flow CRM contact save and vCard export

## Summary
Severity: High
Advisory: CVE-2026-19433
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-19433
Type: osv

## Details
Authorization Bypass Through User-Controlled Key in the contact management component in Roskus Prospero Flow CRM before 5.4.8 allows authenticated users of any company to blindly overwrite the contact data of another company and to download that contact's personal data as a vCard via the contact's numeric identifier, because the save and export operations retrieve the record without constraining the query to the authenticated user's company.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19433.json
- https://github.com/Roskus/prospero-flow-crm/releases/tag/v5.5.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-19433
- https://github.com/Roskus/prospero-flow-crm/commit/f16b4af2027b17bef7c604c92dbd86cf38082398
- https://github.com/Roskus/prospero-flow-crm
- https://secur0.com/en/cna/cve-list/cve-2026-19433-idor-in-prospero-flow-crm-contact-save-and-vcard-export
