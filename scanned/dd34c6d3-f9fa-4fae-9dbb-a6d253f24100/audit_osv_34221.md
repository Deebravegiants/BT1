# [C] CVE-2025-56157

## Summary
Severity: Critical
Advisory: CVE-2025-56157
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-56157
Type: osv

## Details
Default credentials in Dify thru 1.5.1. PostgreSQL username and password specified in the docker-compose.yaml file included in its source code. NOTE: the Supplier reports that the Docker configuration does not make PostgreSQL (on TCP port 5432) exposed by default in version 1.0.1 or later.

## References
- https://gist.github.com/Cristliu/216ddbadaf3258498c93d408683ecabd
- https://gist.github.com/Cristliu/298f51cbc72c45d91632cd0d65aa8161
- https://github.com/langgenius/dify/releases/tag/1.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56157.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56157
- https://github.com/langgenius/dify/issues/15285
- https://github.com/langgenius/dify/pull/15286
- https://github.com/langgenius/dify/pull/15286.diff
- https://github.com/langgenius/dify
