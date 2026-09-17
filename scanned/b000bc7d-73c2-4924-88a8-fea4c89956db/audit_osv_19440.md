# [M] CVE-2021-21313

## Summary
Severity: Medium
Advisory: CVE-2021-21313
Aliases: GHSA-h4hj-mrpg-xfgx
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2021-21313
Type: osv

## Details
GLPI is open source software which stands for Gestionnaire Libre de Parc Informatique and it is a Free Asset and IT Management Software package. In GLPI before verison 9.5.4, there is a vulnerability in the /ajax/common.tabs.php endpoint, indeed, at least two parameters _target and id are not properly sanitized. Here are two payloads (due to two different exploitations depending on which parameter you act) to exploit the vulnerability:/ajax/common.tabs.php?_target=javascript:alert(document.cookie)&_itemtype=DisplayPreference&_glpi_tab=DisplayPreference$2&id=258&displaytype=Ticket (Payload triggered if you click on the button). /ajax/common.tabs.php?_target=/front/ticket.form.php&_itemtype=Ticket&_glpi_tab=Ticket$1&id=(){};(function%20(){alert(document.cookie);})();function%20a&#.

## References
- https://github.com/glpi-project/glpi/releases/tag/9.5.4
- https://github.com/glpi-project/glpi/security/advisories/GHSA-h4hj-mrpg-xfgx
