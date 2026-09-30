# [H] Denial of service in github.com/nats-io/nats-server/server

## Summary
Severity: High
Advisory: GHSA-m4jx-6526-vvhm
CVE: CVE-2020-28466
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-m4jx-6526-vvhm
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server` — affected >=0 <2.2.0
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.2.0

## Details
This affects all versions of package github.com/nats-io/nats-server/server. Untrusted accounts are able to crash the server using configs that represent a service export/import cycles. Disclaimer from the maintainers - Running a NATS service which is exposed to untrusted users presents a heightened risk. Any remote execution flaw or equivalent seriousness, or denial-of-service by unauthenticated users, will lead to prompt releases by the NATS maintainers. Fixes for denial of service issues with no threat of remote execution, when limited to account holders, are likely to just be committed to the main development branch with no special attention. Those who are running such services are encouraged to build regularly from git.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28466
- https://github.com/nats-io/nats-server/pull/1731
- https://github.com/nats-io/nats-server/pull/1731/commits/2e3c22672936f4980d343fb1d328b38919e74796
- https://pkg.go.dev/vuln/GO-2022-0855
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMNATSIONATSSERVERSERVER-1042967
- http://www.openwall.com/lists/oss-security/2021/03/16/1
- http://www.openwall.com/lists/oss-security/2021/03/16/2
