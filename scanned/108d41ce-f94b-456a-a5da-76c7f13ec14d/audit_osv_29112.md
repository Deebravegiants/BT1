# [M] Server crash via Elasticsearch certificate file

## Summary
Severity: Medium
Advisory: CVE-2024-39810
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2024-39810
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.7 and 9.10.x <= 9.10.0 fail to time limit and size limit the CA path file in the ElasticSearch configuration which allows a System Role with access to the Elasticsearch system console to add any file as a CA path field, such as /dev/zero and, after testing the connection, cause the application to crash.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39810.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39810
