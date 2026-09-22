# [M] docker-socket-proxy through 0.5.0 Insufficient Access Control Granularity Exposes Container Filesystems

## Summary
Severity: Medium
Advisory: CVE-2026-78122
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-78122
Type: osv

## Details
docker-socket-proxy fails to properly gate read endpoints in the /containers Docker API namespace when the CONTAINERS environment variable is set. Attackers can use GET requests to /containers/{id}/archive, /containers/{id}/export, /containers/{id}/logs, and /containers/{id}/top to read arbitrary files and download entire container filesystems as tar archives.

## References
- https://hub.docker.com/r/tecnativa/docker-socket-proxy
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78122.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78122
- https://www.vulncheck.com/advisories/docker-socket-proxy-through-insufficient-access-control-granularity-exposes-container-filesystems
- https://github.com/Tecnativa/docker-socket-proxy/issues/182
- https://github.com/Tecnativa/docker-socket-proxy/pull/183
- https://github.com/Tecnativa/docker-socket-proxy
- https://github.com/Tecnativa/docker-socket-proxy/blob/v0.5.0/haproxy.cfg#L49-L61
- https://gist.github.com/nedlir/e4f52f88a757f02c67db1fd5dd70d732
