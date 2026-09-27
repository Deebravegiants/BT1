# [H] SQL Injection in the KubeClarity REST API

## Summary
Severity: High
Advisory: GHSA-5248-h45p-9pgw
CVE: CVE-2024-39909
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-12
Source: https://github.com/advisories/GHSA-5248-h45p-9pgw
Type: github-advisory

## Affected
- Go: `github.com/openclarity/kubeclarity/backend` — affected >=0 <0.0.0-20240711173334-1d1178840703

## Details
### Summary
A time/boolean SQL Injection is present in the following resource `/api/applicationResources` via the following parameter `packageID`

### Details
As it can be seen [here](https://github.com/openclarity/kubeclarity/blob/main/backend/pkg/database/id_view.go#L79), while building the SQL Query the `fmt.Sprintf` function is used to build the query string without the input having first been subjected to any validation.

### PoC
The following command should be able to trigger a basic version of the behavior:
`curl -i -s -k -X $'GET' \
    -H $'Host: kubeclarity.test' \
    $'https://kubeclarity.test/api/applicationResources?page=1&pageSize=50&sortKey=vulnerabilities&sortDir=DESC&packageID=c89973a6-4e7f-50b5-afe2-6bf6f4d3da0a\'HTTP/2'`

### Impact
While using the Helm chart, the impact of this vulnerability is limited since it allows read access only to the kuberclarity database, to which access is already given as far as I understand to regular users anyway.
On the other hand, if Kuberclarity is deployed in a less secure way, this might allow access to more data then allowed or expected (beyond the limits of the KuberClarity database). The vulnerable line was introduced as part of the initial commit of Kubeclarity, so all versions up until the latest (2.23.1) are assumed vulnerable.

## References
- https://github.com/openclarity/kubeclarity/security/advisories/GHSA-5248-h45p-9pgw
- https://nvd.nist.gov/vuln/detail/CVE-2024-39909
- https://github.com/openclarity/kubeclarity/commit/1d1178840703a72d9082b7fc4aea0a3326c5d294
- https://github.com/openclarity/kubeclarity
- https://github.com/openclarity/kubeclarity/blob/main/backend/pkg/database/id_view.go#L79
