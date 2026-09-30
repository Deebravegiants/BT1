# [M] CVE-2020-5248

## Summary
Severity: Medium
Advisory: CVE-2020-5248
Aliases: GHSA-j222-j9mf-h6j9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-05-12
Source: https://osv.dev/vulnerability/CVE-2020-5248
Type: osv

## Details
GLPI before before version 9.4.6 has a vulnerability involving a default encryption key. GLPIKEY is public and is used on every instance. This means anyone can decrypt sensitive data stored using this key. It is possible to change the key before installing GLPI. But on existing instances, data must be reencrypted with the new key. Problem is we can not know which columns or rows in the database are using that; espcially from plugins. Changing the key without updating data would lend in bad password sent from glpi; but storing them again from the UI will work.

## References
- https://github.com/glpi-project/glpi/security/advisories/GHSA-j222-j9mf-h6j9
- https://github.com/glpi-project/glpi/commit/efd14468c92c4da43333aa9735e65fd20cbc7c6c
