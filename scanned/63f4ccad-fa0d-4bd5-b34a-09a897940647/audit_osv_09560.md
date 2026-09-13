# [M] CVE-2017-1000146

## Summary
Severity: Medium
Advisory: CVE-2017-1000146
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-11-03
Source: https://osv.dev/vulnerability/CVE-2017-1000146
Type: osv

## Details
Mahara 1.9 before 1.9.7 and 1.10 before 1.10.5 and 15.04 before 15.04.2 are vulnerable to the arbitrary execution of Javascript in the browser of a logged-in user because the title of the portfolio page was not being properly escaped in the AJAX script that updates the Add/remove watchlist link on artefact detail pages.

## References
- https://bugs.launchpad.net/mahara/+bug/1472439
