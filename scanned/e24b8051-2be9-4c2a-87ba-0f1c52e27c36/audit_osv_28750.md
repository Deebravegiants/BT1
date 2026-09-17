# [C] CVE-2024-36058

## Summary
Severity: Critical
Advisory: CVE-2024-36058
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2024-36058
Type: osv

## Details
The Send Basket functionality in Koha Library before 23.05.10 is susceptible to Time-Based SQL Injection because it fails to sanitize the POST parameter bib_list in /cgi-bin/koha/opac-sendbasket.pl, allowing library users to read arbitrary data from the database.

## References
- https://github.com/hacklantic/Research/tree/main/CVE-2024-36058
- https://gitlab.com/koha-community/Koha/-/blob/23.05.x/misc/release_notes/release_notes_23_05_10.md
- https://gitlab.com/koha-community/Koha/-/blob/23.05.x/misc/release_notes/release_notes_23_05_11.md
- https://koha-community.org/koha-22-05-22-released/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36058.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36058
