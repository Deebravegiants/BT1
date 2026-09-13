# [H] CVE-2023-37154

## Summary
Severity: High
Advisory: CVE-2023-37154
Aliases: GHSA-p3gv-vmpx-hhw4
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2023-37154
Type: osv

## Details
check_by_ssh in Nagios nagios-plugins 2.4.5 allows arbitrary command execution via ProxyCommand, LocalCommand, and PermitLocalCommand with \${IFS}. This has been categorized both as fixed in e8810de, and as intended behavior.

## References
- https://joshua.hu/nagios-hacking-cve-2023-37154
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37154.json
- https://github.com/monitoring-plugins/monitoring-plugins/security/advisories/GHSA-p3gv-vmpx-hhw4
- https://nvd.nist.gov/vuln/detail/CVE-2023-37154
- https://github.com/nagios-plugins/nagios-plugins/commit/e8810de21be80148562b7e0168b0a62aeedffde6
