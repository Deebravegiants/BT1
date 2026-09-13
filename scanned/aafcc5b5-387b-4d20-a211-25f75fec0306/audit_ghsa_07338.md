# [M] Decidim: CSV census record endpoints improper authorization

## Summary
Severity: Medium
Advisory: GHSA-q79h-67vx-m9xg
CVE: CVE-2026-45415
CWE: CWE-285
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-q79h-67vx-m9xg
Type: github-advisory

## Affected
- RubyGems: `decidim-verifications` — affected >=0 <0.30.9
- RubyGems: `decidim-verifications` — affected >=0.31.0.rc1 <0.31.5
- RubyGems: `decidim-verifications` — affected >=0.32.0.rc1 <0.32.0

## Details
## Description

A participant manager can access and modify the CSV census record admin forms.

## Technical description

The CSV census admin record-management surface under `/admin/csv_census/census_logs` does not enforce admin-only authorization before rendering or mutating `Decidim::Verifications::CsvDatum`.

A participant manager (which can only manage participants) can therefore open the admin forms, create or update census rows, and delete rows directly.

Reproduction steps:
1. Sign in a participant admin and open `http://localhost:3000/admin/csv_census/census_logs/new_record` in the browser. Confirm the create form loads even though the session is not a full admin.

<img width="1541" height="274" alt="decidim-census-01" src="https://github.com/user-attachments/assets/859ee101-746f-4acb-8051-27036689f1b3" />

<img width="1538" height="363" alt="decidim-census-02" src="https://github.com/user-attachments/assets/85bbb004-a999-46dc-856c-fd32b50ced2c" />

Note that normal participant accounts were not able to access the CSV census records which is good.

### Impact
 
Any participant admin can create, alter, or remove CSV census rows, which can corrupt verification data relied on by authorization workflows.

### Patches

See https://github.com/decidim/decidim/pull/16674 and https://github.com/decidim/decidim/pull/16703 

### Workarounds

Disable Organization Census verification method

### Reference

OWASP A01:2021 Broken Access Control

### Credits

This issue was discovered in a security audit organized by the [Decidim Association](https://decidim.org) and made by [Radically Open Security](https://www.radicallyopensecurity.com/) against Decidim financed by [NGI](https://ngi.eu/).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-q79h-67vx-m9xg
- https://github.com/decidim/decidim/pull/16674
- https://github.com/decidim/decidim/pull/16703
- https://github.com/decidim/decidim
