# [H] JuiceFS - Authentication Bypass via pprof and metrics Endpoints

## Summary
Severity: High
Advisory: CVE-2026-59092
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-59092
Type: osv

## Details
JuiceFS through 1.3.1, fixed in commit a46979c, contains an authentication bypass vulnerability that allows unauthenticated remote attackers to access sensitive debug and metrics endpoints by exploiting improper handler registration on the shared http.DefaultServeMux. Attackers can request the /debug/pprof/cmdline endpoint to obtain the process command line containing metadata engine connection strings with database credentials, granting full read/write access to filesystem metadata, while other pprof handlers leak internal state and profiling handlers enable denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59092.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59092
- https://www.vulncheck.com/advisories/juicefs-authentication-bypass-via-pprof-and-metrics-endpoints
- https://github.com/juicedata/juicefs/pull/7214
- https://github.com/juicedata/juicefs/commit/a46979cdd4082217081ee99b931ddc53d038e47a
- https://github.com/juicedata/juicefs
- https://github.com/juicedata/juicefs/issues/7213
