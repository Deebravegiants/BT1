# [C] CVE-2022-31733

## Summary
Severity: Critical
Advisory: CVE-2022-31733
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-02-03
Source: https://osv.dev/vulnerability/CVE-2022-31733
Type: osv

## Details
Starting with diego-release 2.55.0 and up to 2.69.0, and starting with CF Deployment 17.1 and up to 23.2.0, apps are accessible via another port on diego cells, allowing application ingress without a client certificate. If mTLS route integrity is enabled AND unproxied ports are turned off, then an attacker could connect to an application that should be only reachable via mTLS, without presenting a client certificate.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31733.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-31733
- https://www.cloudfoundry.org/blog/cve-2022-31733-unsecured-application-port
