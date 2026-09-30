# [M] KubeEdge CloudCore through 1.23.1 Missing Authentication on Node Task Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-82473
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82473
Type: osv

## Details
KubeEdge CloudCore through 1.23.1 accepts node task status reports on its HTTPS server without authentication verification. Attackers can reach CloudCore on port 10002 to mark upgrade jobs as succeeded or failed, deceiving the control plane about node upgrade status and blocking further upgrade scheduling.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82473.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82473
- https://www.vulncheck.com/advisories/kubeedge-cloudcore-through-1.23.1-missing-authentication-on-node-task-endpoints
- https://github.com/kubeedge/kubeedge
- https://github.com/kubeedge/kubeedge/blob/v1.23.1/cloud/pkg/cloudhub/servers/httpserver/nodetask/report_status.go
- https://github.com/kubeedge/kubeedge/blob/v1.23.1/cloud/pkg/cloudhub/servers/httpserver/server.go
- https://github.com/geo-chen/oss/blob/main/kubeedge.md
