# [H] Grafana Data source and plugin proxy endpoints could leak the authentication cookie to some destination plugins

## Summary
Severity: High
Advisory: GHSA-x744-mm8v-vpgr
CVE: CVE-2022-39201
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-x744-mm8v-vpgr
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=5.0.0-beta1 <8.5.14
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.1.8

## Details
Today we are releasing Grafana 9.2. Alongside with new features and other bug fixes, this release includes a Moderate severity security fix for CVE-2022-39201

We are also releasing security patches for Grafana 9.1.8 and Grafana 8.5.14 to fix these issues.

Release 9.2, latest release, also containing security fix:

- [Download Grafana 9.2](https://grafana.com/grafana/download/9.2)

Release 9.1.8, only containing security fix:

- [Download Grafana 9.1.8](https://grafana.com/grafana/download/9.1.8)

Release 8.5.14, only containing security fix:

- [Download Grafana 8.5.14](https://grafana.com/grafana/download/8.5.14)

Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud) and as always, we closely coordinated with all cloud providers licensed to offer Grafana Pro. They have received early notification under embargo and confirmed that their offerings are secure at the time of this announcement. This is applicable to Amazon Managed Grafana and Azure's Grafana as a service offering.

## CVE-2022-39201

### Summary
On September 7th as a result of an internal security audit we have discovered that Grafana could leak the authentication cookie of users to plugins. After further analysis the vulnerability impacts data source and plugin proxy endpoints under certain conditions.

We believe that this vulnerability is rated at CVSS 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)

### Impact
The destination plugin could receive a Grafana authentication cookie of the user.

### Impacted versions

All installations for Grafana versions >= v5.0.0-beta1

### Solutions and mitigations

To fully address CVE-2022-39201 please upgrade your Grafana instances. 
Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud).

### Reporting security issues

If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

### Security announcements

We maintain a [security category](https://community.grafana.com/c/support/security-announcements) on our blog, where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-x744-mm8v-vpgr
- https://nvd.nist.gov/vuln/detail/CVE-2022-39201
- https://github.com/grafana/grafana/commit/b571acc1dc130a33f24742c1f93b93216da6cf57
- https://github.com/grafana/grafana/commit/c658816f5229d17f877579250c07799d3bbaebc9
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/releases/tag/v9.1.8
