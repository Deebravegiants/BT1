# [C] Remote Code Execution via `/apply_settings` and `/execute_code` in parisneo/lollms-webui

## Summary
Severity: Critical
Advisory: CVE-2024-4326
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/CVE-2024-4326
Type: osv

## Details
A vulnerability in parisneo/lollms-webui versions up to 9.3 allows remote attackers to execute arbitrary code. The vulnerability stems from insufficient protection of the `/apply_settings` and `/execute_code` endpoints. Attackers can bypass protections by setting the host to localhost, enabling code execution, and disabling code validation through the `/apply_settings` endpoint. Subsequently, arbitrary commands can be executed remotely via the `/execute_code` endpoint, exploiting the delay in settings enforcement. This issue was addressed in version 9.5.

## References
- https://huntr.com/bounties/2ab9f03d-0538-4317-be21-0748a079cbdd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4326.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4326
- https://github.com/parisneo/lollms-webui/commit/abb4c6d495a95a3ef5b114ffc57f85cd650b905e
