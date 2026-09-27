# [H] Cacti: SQL Injection in managers.php

## Summary
Severity: High
Advisory: CVE-2026-40083
Aliases: GHSA-j9jv-6xjq-9hhj
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-40083
Type: osv

## Details
Cacti is an open source performance and fault management framework. Versions 1.2.30 and prior have SQL Injection through unsanitized unserialize+implode in managers.php.  At line 756 of managers.php, the application assigns $selected_items by calling cacti_unserialize(stripslashes(gnrv('selected_graphs_array'))). The  cacti_unserialize() function calls unserialize() with allowed_classes set to false, which prevents object injection but still allows arbitrary string  arrays to be deserialized. Then, at lines 760 to 766, the deserialized array values are passed directly into db_execute('DELETE FROM snmpagent_managers  WHERE id IN (' . implode(',', $selected_items) . ')'), where they are imploded into the SQL statement without any integer validation, resulting in SQL  Injection when using SNMP agent management permissions. This issue has been fixed in version 1.2.31.

## References
- https://github.com/Cacti/cacti/releases/tag/release%2F1.2.31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40083.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-j9jv-6xjq-9hhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-40083
