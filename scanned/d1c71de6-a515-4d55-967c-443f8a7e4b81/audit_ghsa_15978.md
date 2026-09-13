# [M] open-webui allows writing and deleting arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-54f4-v6v9-9q82
CVE: CVE-2024-7037
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-10-09
Source: https://github.com/advisories/GHSA-54f4-v6v9-9q82
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
In version v0.3.8 of open-webui/open-webui, the endpoint /api/pipelines/upload is vulnerable to arbitrary file write and delete due to unsanitized file.filename concatenation with CACHE_DIR. This vulnerability allows attackers to overwrite and delete system files, potentially leading to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7037
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/blob/main/backend/main.py#L1513
- https://huntr.com/bounties/8508db68-9c99-4b1c-828c-e1bfcacfb847
