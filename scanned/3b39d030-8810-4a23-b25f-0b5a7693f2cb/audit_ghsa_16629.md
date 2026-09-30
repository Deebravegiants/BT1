# [C] Grafana Fine-grained access control vulnerability

## Summary
Severity: Critical
Advisory: GHSA-mpwp-42x6-4wmx
CVE: CVE-2021-41244
CWE: CWE-610, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-mpwp-42x6-4wmx
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=8.0.0 <8.2.4

## Details
### Impact
On Nov. 2, during an internal security audit, we discovered that when the fine-grained access control beta feature is enabled and there is more than one organization in the Grafana instance, Grafana 8.0 introduced a mechanism which allowed users with the Organization Admin role to list, add, remove, and update users’ roles in other organizations in which they are not an admin.

### Patches
Fixed in 8.2.4

### Workarounds
All installations between v8.0 and v8.2.3 that have fine-grained access control beta enabled and more than one organization should be upgraded as soon as possible. If you cannot upgrade, you should turn off the fine-grained access control using a [feature flag](https://grafana.com/docs/grafana/latest/enterprise/access-control/#enable-fine-grained-access-control/).

Grafana Cloud instances have not been affected by the vulnerability.

### Reporting security issues
If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

### Security announcements

We maintain a [security category on our blog](https://grafana.com/tags/security/), where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-mpwp-42x6-4wmx
- https://nvd.nist.gov/vuln/detail/CVE-2021-41244
- https://github.com/grafana/grafana
- https://grafana.com/blog/2021/11/15/grafana-8.2.4-released-with-security-fixes
- https://security.netapp.com/advisory/ntap-20211223-0001
- http://www.openwall.com/lists/oss-security/2021/11/15/1
