# [H] Grafana User enumeration via forget password

## Summary
Severity: High
Advisory: GHSA-3p62-42x7-gxg5
CVE: CVE-2022-39307
CWE: CWE-200, CWE-209
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-3p62-42x7-gxg5
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.2.4
- Go: `github.com/grafana/grafana` — affected >=0 <8.5.15

## Details
Today we are releasing Grafana 9.2.4. Alongside other bug fixes, this patch release includes moderate security fixes for CVE-2022-39307.

We are also releasing security patches for Grafana 8.5.15 to fix these issues.

Release 9.2.4, latest patch, also containing security fix:

- [Download Grafana 9.2.4](https://grafana.com/grafana/download/9.2.4)

Release 8.5.15, only containing security fix:

- [Download Grafana 8.5.15](https://grafana.com/grafana/download/8.5.15)

Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud) and as always, we closely coordinated with all cloud providers licensed to offer Grafana Pro. They have received early notification under embargo and confirmed that their offerings are secure at the time of this announcement. This is applicable to Amazon Managed Grafana and Azure Managed Grafana as a service offering.

## Username enumeration

### Summary 

When using the forget password on the login page, a POST request is made to the `/api/user/password/sent-reset-email` URL. When the username or email does not exist, a JSON response contains a “user not found” message.

The CVSS score for this vulnerability is [5.3 Moderate](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N&version=3.1)

### Impact

The impacted endpoint leaks information to unauthenticated users and introduces a security risk.

### Impacted versions

All installations for Grafana versions Grafana <=9.x, <8.x

### Solutions and mitigations

To fully address CVE-2022-39307, please upgrade your Grafana instances. 
Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud). 

## Reporting security issues

If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

## Security announcements

We maintain a [security category](https://community.grafana.com/c/support/security-announcements) on our blog, where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-3p62-42x7-gxg5
- https://nvd.nist.gov/vuln/detail/CVE-2022-39307
- https://github.com/grafana/grafana
- https://security.netapp.com/advisory/ntap-20221215-0004
