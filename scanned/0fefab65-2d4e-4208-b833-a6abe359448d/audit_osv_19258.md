# [H] CVE-2020-9381

## Summary
Severity: High
Advisory: CVE-2020-9381
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-02-24
Source: https://osv.dev/vulnerability/CVE-2020-9381
Type: osv

## Details
controllers/admin.js in Total.js CMS 13 allows remote attackers to execute arbitrary code via a POST to the /admin/api/widgets/ URI. This can be exploited in conjunction with CVE-2019-15954.

## References
- https://github.com/totaljs/cms/commit/2a26c4c6a61d3fda4527a761716ef7e1c5f7c970
- https://github.com/saddean/research/blob/master/totaljs/Broken-acces-control.md
