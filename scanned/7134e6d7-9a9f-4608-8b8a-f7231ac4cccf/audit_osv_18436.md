# [M] CVE-2020-27662

## Summary
Severity: Medium
Advisory: CVE-2020-27662
Aliases: GHSA-wq38-gwxp-8p5p
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-11-26
Source: https://osv.dev/vulnerability/CVE-2020-27662
Type: osv

## Details
In GLPI before 9.5.3, ajax/comments.php has an Insecure Direct Object Reference (IDOR) vulnerability that allows an attacker to read data from any database table (e.g., glpi_tickets, glpi_users, etc.).

## References
- https://github.com/glpi-project/glpi/security/advisories/GHSA-wq38-gwxp-8p5p
