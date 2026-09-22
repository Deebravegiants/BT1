# [H] CVE-2019-13967

## Summary
Severity: High
Advisory: CVE-2019-13967
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-14
Source: https://osv.dev/vulnerability/CVE-2019-13967
Type: osv

## Details
iTop 2.2.0 through 2.6.0 allows remote attackers to cause a denial of service (application outage) via many requests to launch a compile operation. The requests use the pages/exec.php?exec_env=production&exec_module=itop-hub-connector&exec_page=ajax.php&operation=compile URI. This only affects the community version.

## References
- https://0day.love/itop_vulnerabilities_disclosure.pdf
- https://www.itophub.io/wiki/page?id=latest%3Arelease%3Achange_log
