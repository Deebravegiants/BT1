# [M] CVE-2025-63681

## Summary
Severity: Medium
Advisory: CVE-2025-63681
Aliases: GHSA-frv8-gffc-37px, PYSEC-2026-1732
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-63681
Type: osv

## Details
open-webui v0.6.33 is vulnerable to Incorrect Access Control. The API /api/tasks/stop/ directly accesses and cancels tasks without verifying user ownership, enabling attackers (a normal user) to stop arbitrary LLM response tasks.

## References
- https://github.com/TOAST-Research/pocs/blob/main/openwebui/arbitirary_task_stop/report.md
- https://github.com/open-webui/open-webui/blob/46ae3f4f5d7d4d706041bdae4ad2d802e568712b/backend/open_webui/main.py#L1652
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63681.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63681
