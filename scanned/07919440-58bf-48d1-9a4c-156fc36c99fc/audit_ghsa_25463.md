# [H] furlongm openvpn-monitor command injection

## Summary
Severity: High
Advisory: GHSA-4258-vcjw-wwxx
CVE: CVE-2021-31605
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4258-vcjw-wwxx
Type: github-advisory

## Affected
- PyPI: `openvpn-monitor` — affected >=0

## Details
furlongm openvpn-monitor through 1.1.3 allows `%0a` command injection via the OpenVPN management interface socket. This can shut down the server via signal `SIGTERM`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31605
- https://github.com/furlongm/openvpn-monitor
- https://github.com/furlongm/openvpn-monitor/releases
- https://github.com/pypa/advisory-database/tree/main/vulns/openvpn-monitor/PYSEC-2021-353.yaml
- http://packetstormsecurity.com/files/164278/OpenVPN-Monitor-1.1.3-Command-Injection.html
