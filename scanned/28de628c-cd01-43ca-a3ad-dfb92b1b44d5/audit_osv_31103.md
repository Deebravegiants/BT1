# [C] CVE-2024-57971

## Summary
Severity: Critical
Advisory: CVE-2024-57971
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-16
Source: https://osv.dev/vulnerability/CVE-2024-57971
Type: osv

## Details
DataSourceResource.java in the SpagoBI API support in Knowage Server in KNOWAGE before 8.1.30 does not ensure that java:comp/env/jdbc/ occurs at the beginning of a JNDI Name.

## References
- https://github.com/KnowageLabs/Knowage-Server/compare/v8.1.29...v8.1.30
- https://github.com/darumaseye/CVEs/blob/ec2de9f7ecffde466e687745bfdfc672e86241d7/CVE-2024-57971.md
- https://spagobi.readthedocs.io
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57971.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57971
- https://github.com/KnowageLabs/Knowage-Server/commit/f7d0362f737e1b0db1cc9cc95b1236d62d83dd0c
