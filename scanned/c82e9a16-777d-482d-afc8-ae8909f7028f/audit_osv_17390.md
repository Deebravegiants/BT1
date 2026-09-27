# [H] CVE-2020-14947

## Summary
Severity: High
Advisory: CVE-2020-14947
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-14947
Type: osv

## Details
OCS Inventory NG 2.7 allows Remote Command Execution via shell metacharacters to require/commandLine/CommandLine.php because mib_file in plugins/main_sections/ms_config/ms_snmp_config.php is mishandled in get_mib_oid.

## References
- https://github.com/OCSInventory-NG/OCSInventory-ocsreports/commit/da72e0fddaeceee44fbbd7241e07e5d53d1eee64
- http://packetstormsecurity.com/files/158293/OCS-Inventory-NG-2.7-Remote-Code-Execution.html
- https://drive.google.com/file/d/1-LVfL5ui5m2QfQxr0fDopzSECd4fTNrQ/view?usp=sharing
- https://gist.github.com/mhaskar/233436d3096d4a7beafe36ff61dc2c73
- https://shells.systems/ocs-inventory-ng-v2-7-remote-command-execution-cve-2020-14947/
