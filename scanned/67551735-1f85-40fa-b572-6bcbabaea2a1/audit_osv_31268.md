# [M] IDOR in open-webui/open-webui

## Summary
Severity: Medium
Advisory: CVE-2024-7048
CVSS: 6.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-10-10
Source: https://osv.dev/vulnerability/CVE-2024-7048
Type: osv

## Details
In version v0.3.8 of open-webui, an improper privilege management vulnerability exists in the API endpoints GET /api/v1/documents/ and POST /rag/api/v1/doc. This vulnerability allows a lower-privileged user to access and overwrite files managed by a higher-privileged admin. By exploiting this vulnerability, an attacker can view metadata of files uploaded by an admin and overwrite these files, compromising the integrity and availability of the RAG models.

## References
- https://huntr.com/bounties/acd0b2dd-61eb-4712-82d3-a4e35d6ee560
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7048.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7048
