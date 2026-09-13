# [C] CVE-2026-31215

## Summary
Severity: Critical
Advisory: CVE-2026-31215
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-31215
Type: osv

## Details
The nexent v1.7.5.2 backend service contains an unauthorized arbitrary file deletion vulnerability in its ElasticSearch service interface. The DELETE /{index_name}/documents endpoint lacks proper authentication and authorization controls and does not validate the user-supplied path_or_url parameter. This allows unauthenticated remote attackers to send crafted requests that trigger the deletion of arbitrary documents from ElasticSearch indices and corresponding files from the MinIO storage system. Successful exploitation leads to data destruction and denial of service.

## References
- https://www.notion.so/CVE-2026-31215-35d1e139318881f5946ed206d96e34d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31215.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31215
- https://github.com/ModelEngine-Group/nexent
