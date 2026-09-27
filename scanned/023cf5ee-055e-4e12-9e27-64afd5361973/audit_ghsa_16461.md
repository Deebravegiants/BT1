# [M] Grafana Data source and plugin proxy endpoints leaking authentication tokens to some destination plugins

## Summary
Severity: Medium
Advisory: GHSA-jv32-5578-pxjc
CVE: CVE-2022-31130
CWE: CWE-200, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-jv32-5578-pxjc
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.1.8
- Go: `github.com/grafana/grafana` — affected >=7.0.0 <8.5.14

## Details
Today we are releasing Grafana 9.2. Alongside with new features and other bug fixes, this release includes a Moderate severity security fix for CVE-2022-31130

We are also releasing security patches for Grafana 9.1.8 and Grafana 8.5.14 to fix these issues.

Release 9.2, latest release, also containing security fix:

- [Download Grafana 9.2](https://grafana.com/grafana/download/9.2)

Release 9.1.8, only containing security fix:

- [Download Grafana 9.1.8](https://grafana.com/grafana/download/9.1.8)

Release 8.5.14, only containing security fix:

- [Download Grafana 8.5.14](https://grafana.com/grafana/download/8.5.14)

Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud) and as always, we closely coordinated with all cloud providers licensed to offer Grafana Pro. They have received early notification under embargo and confirmed that their offerings are secure at the time of this announcement. This is applicable to Amazon Managed Grafana and Azure's Grafana as a service offering.

## CVE-2022-31130

### Summary
On June 26 a security researcher contacted Grafana Labs to disclose a vulnerability with the GitLab data source plugin that could leak the API key to GitLab. After further analysis the vulnerability impacts data source and plugin proxy endpoints with authentication tokens but under some conditions.

We believe that this vulnerability is rated at CVSS 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)

### Impact
The destination plugin could receive a Grafana authentication token of the user.

### Impacted versions

All installations for Grafana versions <=9.x, <=8.x, <=7.x

### Solutions and mitigations

To fully address CVE-2022-31130 please upgrade your Grafana instances. 
Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud).

As a workaround do not use API keys, JWT authentication or any HTTP Header based authentication.

### Reporting security issues

If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

### Security announcements

We maintain a [security category](https://community.grafana.com/c/support/security-announcements) on our blog, where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-jv32-5578-pxjc
- https://nvd.nist.gov/vuln/detail/CVE-2022-31130
- https://github.com/grafana/grafana/commit/4dd56e4dabce10007bf4ba1059bf54178c35b177
- https://github.com/grafana/grafana/commit/9da278c044ba605eb5a1886c48df9a2cb0d3885f
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/releases/tag/v9.1.8
