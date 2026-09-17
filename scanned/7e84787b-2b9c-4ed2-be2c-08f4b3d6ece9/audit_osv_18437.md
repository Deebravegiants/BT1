# [M] CVE-2020-27663

## Summary
Severity: Medium
Advisory: CVE-2020-27663
Aliases: GHSA-pqfv-4pvr-55r4
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-11-26
Source: https://osv.dev/vulnerability/CVE-2020-27663
Type: osv

## Details
In GLPI before 9.5.3, ajax/getDropdownValue.php has an Insecure Direct Object Reference (IDOR) vulnerability that allows an attacker to read data from any itemType (e.g., Ticket, Users, etc.).

## References
- https://github.com/glpi-project/glpi/security/advisories/GHSA-pqfv-4pvr-55r4
