# [M] Milvus 2.6.22, 3.0.0 Unauthenticated Denial of Service via /management/stop

## Summary
Severity: Medium
Advisory: CVE-2026-69111
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-69111
Type: osv

## Details
Milvus through 2.6.22 and 3.0.0 contains an unauthenticated denial of service vulnerability that allows remote attackers to terminate service components by sending a crafted HTTP GET request to the management server on port 9091. Attackers can exploit the unprotected /management/stop endpoint, which bypasses REST API authentication middleware, by supplying a 'role' parameter to shut down the proxy, datanode, or querynode components, resulting in denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69111
- https://www.vulncheck.com/advisories/milvus-unauthenticated-denial-of-service-via-management-stop
- https://github.com/milvus-io/milvus/pull/49847
- https://github.com/milvus-io/milvus/pull/51573
- https://github.com/milvus-io/milvus
- https://github.com/milvus-io/milvus/issues/50763
