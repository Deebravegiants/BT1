# [C] UpTrain vulnerable to Remote code execution at `/create_project`

## Summary
Severity: Critical
Advisory: CVE-2025-27770
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2025-27770
Type: osv

## Details
UpTrain is an open-source platform to evaluate and improve generative AI applications. In version 0.7.1 and prior, the `/create_project` endpoint is vulnerable to remote code execution via the `checks` and `metadata` parameters. Any user that has access to UpTrain and a valid authentication method may be able to execute arbitrary code in the context of the host running UpTrain, which in most cases will be the docker container as suggested by the documentation. As of time of publication, no known patch is available.

## References
- https://github.com/uptrain-ai/uptrain/blob/a31cc14eddcb6c0b0b12cbed15f086d98c441c6f/uptrain/dashboard/backend/app.py#L691C22-L691C36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27770.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27770
- https://securitylab.github.com/advisories/GHSL-2024-198_GHSL-2024-199_Uptrain/
