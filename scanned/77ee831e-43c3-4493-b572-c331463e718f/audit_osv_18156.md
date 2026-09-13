# [H] CVE-2020-24617

## Summary
Severity: High
Advisory: CVE-2020-24617
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-19
Source: https://osv.dev/vulnerability/CVE-2020-24617
Type: osv

## Details
Mailtrain through 1.24.1 allows SQL Injection in statsClickedSubscribersByColumn in lib/models/campaigns.js via /campaigns/clicked/ajax because variable column names are not properly escaped.

## References
- https://github.com/Mailtrain-org/mailtrain/pull/909
- https://securitylab.github.com/advisories/GHSL-2020-132-Mailtrain
