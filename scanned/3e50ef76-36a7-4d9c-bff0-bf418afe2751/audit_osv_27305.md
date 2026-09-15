# [M] Uncontrolled Resource Consumption in parisneo/lollms-webui

## Summary
Severity: Medium
Advisory: CVE-2024-1569
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-1569
Type: osv

## Details
parisneo/lollms-webui is vulnerable to a denial of service (DoS) attack due to uncontrolled resource consumption. Attackers can exploit the `/open_code_in_vs_code` and similar endpoints without authentication by sending repeated HTTP POST requests, leading to the opening of Visual Studio Code or the default folder opener (e.g., File Explorer, xdg-open) multiple times. This can render the host machine unusable by exhausting system resources. The vulnerability is present in the latest version of the software.

## References
- https://huntr.com/bounties/369d1694-47e4-49bc-bb35-931ce4a5148e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1569.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1569
- https://github.com/parisneo/lollms-webui/commit/354cf766835396b7fc0d5105ed3b77572a653149
