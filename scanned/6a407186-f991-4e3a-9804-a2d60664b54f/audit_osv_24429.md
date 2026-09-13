# [H] CVE-2023-20881

## Summary
Severity: High
Advisory: CVE-2023-20881
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-05-19
Source: https://osv.dev/vulnerability/CVE-2023-20881
Type: osv

## Details
Cloud foundry instances having CAPI version between 1.140 and 1.152.0 along with loggregator-agent v7+ may override other users syslog drain credentials if they're aware of the client certificate used for that syslog drain. This applies even if the drain has zero certs. This would allow the user to override the private key and add or modify a certificate authority used for the connection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/20xxx/CVE-2023-20881.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-20881
- https://www.cloudfoundry.org/blog/cve-2023-20881-cas-for-syslog-drain-mtls-feature-can-be-overwritten/
