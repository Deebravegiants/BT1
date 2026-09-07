# [H] Grafana Escalation from admin to server admin when auth proxy is used

## Summary
Severity: High
Advisory: GHSA-ff5c-938w-8c9q
CVE: CVE-2022-35957
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-ff5c-938w-8c9q
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=9.1.0 <9.1.6
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.0.9
- Go: `github.com/grafana/grafana` — affected >=0 <8.5.13

## Details
Today we are releasing Grafana 9.1.6, 9.0.9, 8.5.13. This patch release includes a Moderate severity security fix for CVE-2022-35957 that affects Grafana instances which are using Grafana [Auth Proxy](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/auth-proxy/#configure-auth-proxy-authentication).

Release 9.1.6, latest patch, also containing security fix:

- [Download Grafana 9.1.6](https://grafana.com/grafana/download/9.1.6)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-9-1-6/)

Release 9.0.9, only containing security fix:

- [Download Grafana 9.0.9](https://grafana.com/grafana/download/9.0.9)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-9-0-9/)

Release 8.5.13, only containing security fix:

- [Download Grafana 8.5.13](https://grafana.com/grafana/download/8.5.13)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-8-5-13/)

Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud) and as always, we closely coordinated with all cloud providers licensed to offer Grafana Pro. They have received early notification under embargo and confirmed that their offerings are secure at the time of this announcement. This is applicable to Amazon Managed Grafana and Azure's Grafana as a service offering.

## Privilege escalation (CVE-2022-35957)

### Summary 

On August 9 an internal security review identified a vulnerability in the Grafana which allows an escalation from Admin privileges to Server Admin when Auth proxy authentication is used.

[Auth proxy](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/auth-proxy/#configure-auth-proxy-authentication) allows to authenticate a user by only providing the username (or email) in a `X-WEBAUTH-USER` HTTP header: the trust assumption is that a front proxy will take care of authentication and that Grafana server is publicly reachable only with this front proxy.

[Datasource proxy](https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#data-source-proxy-calls) breaks this assumption:
- it is possible to configure a fake datasource pointing to a localhost Grafana install with a `X-WEBAUTH-USER` HTTP header containing admin username.
- This fake datasource can be called publicly via this proxying feature.

The CVSS score for this vulnerability is 6.6 Moderate (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H).

### Impacted versions

All Grafana installations where the [Auth Proxy](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/auth-proxy/#configure-auth-proxy-authentication) is used.

### Solutions and mitigations

To fully address CVE-2022-35957 please upgrade your Grafana instances. They are only required if you are using Auth proxy. If you can’t upgrade, as an alternative, you can deactivate the auth proxy. 

Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud).

### Timeline

Here is a timeline starting from when we originally learned of the issue. 

* 2022-08-09: Vulnerability is reported as a result of an Internal security audit.
* 2022-08-09: Release timeline determined: 2022-09-06 for private customer release, 2022-09-20 for public release.
* 2022-08-09: Confirmed that Grafana Cloud is not impacted.
* 2022-09-06: Private release.
* 2022-09-20: Public release.

## Reporting security issues

If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

## Security announcements

We maintain a [security category](https://community.grafana.com/c/support/security-announcements) on our blog, where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-ff5c-938w-8c9q
- https://nvd.nist.gov/vuln/detail/CVE-2022-35957
- https://github.com/grafana/grafana
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WYU5C2RITLHVZSTCWNGQWA6KSPYNXM2H
- https://security.netapp.com/advisory/ntap-20221215-0001
