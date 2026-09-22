# [H] CVE-2020-15876

## Summary
Severity: High
Advisory: CVE-2020-15876
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2020-15876
Type: osv

## Details
An issue was discovered in LibreNMS 1.65. A remote authenticated attacker with normal privileges can extract all the information from the LibreNMS database via a SQL injection in the sort parameter in the /ajax_table.php API endpoint. This affects address-search.inc.php, alertlog.inc.php, arp-search.inc.php, as-selection.inc.php, bills.inc.php, device_mibs.inc.php, device_oids.inc.php, edit-ports.inc.php, eventlog.inc.php, inventory.inc.php, ix-list.inc.php, ix-peers.inc.php, mempool-edit.inc.php, mempool.inc.php, mibs.inc.php, poll-log.inc.php, processor-edit.inc.php, processor.inc.php, routing-edit.inc.php, sensors-common.inc.php, storage-edit.inc.php, storage.inc.php, tnmsneinfo.inc.php, and toner.inc.php (in includes/html/table).

## References
- https://community.librenms.org/c/announcements
- https://github.com/librenms/librenms/compare/1.65...1.65.1
- https://github.com/librenms/librenms/releases/tag/1.65.1
- https://www.shielder.com/advisories/librenms-searchphrase-authenticated-sql-injection/
- https://shielder.it/blog
