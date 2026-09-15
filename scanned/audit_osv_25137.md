# [M] Beats, Elastic Agent, APM Server, and Fleet Server Improper Certificate Validation issue

## Summary
Severity: Medium
Advisory: CVE-2023-31421
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-26
Source: https://osv.dev/vulnerability/CVE-2023-31421
Type: osv

## Details
It was discovered that when acting as TLS clients, Beats, Elastic Agent, APM Server, and Fleet Server did not verify whether the server certificate is valid for the target IP address; however, certificate signature validation is still performed. More specifically, when the client is configured to connect to an IP address (instead of a hostname) it does not validate the server certificate's IP SAN values against that IP address and certificate validation fails, and therefore the connection is not blocked as expected.

## References
- https://discuss.elastic.co/t/beats-elastic-agent-apm-server-and-fleet-server-8-10-1-security-update-improper-certificate-validation-issue-esa-2023-16/343385
- https://www.elastic.co/community/security
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31421.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31421
