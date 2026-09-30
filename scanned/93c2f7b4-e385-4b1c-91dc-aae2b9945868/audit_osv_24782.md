# [H] CVE-2023-26735

## Summary
Severity: High
Advisory: CVE-2023-26735
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/CVE-2023-26735
Type: osv

## Details
blackbox_exporter v0.23.0 was discovered to contain an access control issue in its probe interface. This vulnerability allows attackers to detect intranet ports and services, as well as download resources. NOTE: this is disputed by third parties because authentication can be configured.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26735.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26735
- https://github.com/prometheus/blackbox_exporter/issues/1024
- https://github.com/prometheus/blackbox_exporter/issues/1025
- https://github.com/prometheus/blackbox_exporter/issues/1026
- https://github.com/prometheus/blackbox_exporter#tls-and-basic-authentication
