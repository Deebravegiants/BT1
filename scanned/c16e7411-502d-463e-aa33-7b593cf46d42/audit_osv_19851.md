# [C] CVE-2021-26830

## Summary
Severity: Critical
Advisory: CVE-2021-26830
Aliases: GHSA-w4f3-7f7c-x652
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-04-16
Source: https://osv.dev/vulnerability/CVE-2021-26830
Type: osv

## Details
SQL Injection in Tribalsystems Zenario CMS 8.8.52729 allows remote attackers to access the database or delete the plugin. This is accomplished via the `ID` input field of ajax.php in the `Pugin library - delete` module.

## References
- https://github.com/TribalSystems/Zenario/releases/tag/8.8.53370
