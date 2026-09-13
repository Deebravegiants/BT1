# [H] piraeus-operator allows attacker to impersonate service account

## Summary
Severity: High
Advisory: GHSA-6fg2-hvj9-832f
CVE: CVE-2024-33398
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-6fg2-hvj9-832f
Type: github-advisory

## Affected
- Go: `github.com/piraeusdatastore/piraeus-operator/v2` — affected >=0

## Details
There is a ClusterRole in piraeus-operator v2.5.0 and earlier which has been granted list secrets permission, which allows an attacker to impersonate the service account bound to this ClusterRole and use its high-risk privileges to list confidential information across the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33398
- https://gist.github.com/HouqiyuA/d0c11fae5ba4789946ae33175d0f9edb
- https://github.com/HouqiyuA/k8s-rbac-poc
- https://github.com/piraeusdatastore/piraeus-operator
- https://piraeus.io
