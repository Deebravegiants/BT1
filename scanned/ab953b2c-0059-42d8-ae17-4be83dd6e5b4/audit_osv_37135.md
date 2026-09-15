# [C] openDCIM <= 23.04 SQL Injection in Config::UpdateParameter

## Summary
Severity: Critical
Advisory: CVE-2026-28516
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28516
Type: osv

## Details
openDCIM version 23.04, through commit 4467e9c4, contains a SQL injection vulnerability in Config::UpdateParameter. The install.php and container-install.php handlers pass user-supplied input directly into SQL statements using string interpolation without prepared statements or proper input sanitation. An authenticated user can execute arbitrary SQL statements against the underlying database.

## References
- https://github.com/opendcim/openDCIM/blob/4467e9c4/config.inc.php#L75-L90
- https://github.com/opendcim/openDCIM/blob/4467e9c4/install.php#L420-L434
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28516.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28516
- https://www.vulncheck.com/advisories/opendcim-sql-injection-in-config-updateparameter
- https://github.com/opendcim/openDCIM/pull/1664
- https://github.com/opendcim/openDCIM/pull/1664/changes/8f7ab2a710086a9c8c269560793e47c577ddda09
- https://github.com/opendcim/openDCIM
- https://chocapikk.com/posts/2026/opendcim-sqli-to-rce/
- https://github.com/Chocapikk/opendcim-exploit
