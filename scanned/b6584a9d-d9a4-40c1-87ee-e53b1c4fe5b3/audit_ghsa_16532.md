# [M] Grafana when using email as a username can block other users from signing in

## Summary
Severity: Medium
Advisory: GHSA-gj7m-853r-289r
CVE: CVE-2022-39229
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-gj7m-853r-289r
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <8.5.14
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.1.8

## Details
Today we are releasing Grafana 9.2. Alongside with new features and other bug fixes, this release includes a Moderate severity security fix for CVE-2022-39229 

We are also releasing security patches for Grafana 9.1.8 and Grafana 8.5.14 to fix these issues.

Release 9.2, latest release, also containing security fix:

- [Download Grafana 9.2](https://grafana.com/grafana/download/9.2)

Release 9.1.8, only containing security fix:

- [Download Grafana 9.1.8](https://grafana.com/grafana/download/9.1.8)

Release 8.5.14, only containing security fix:

- [Download Grafana 8.5.14](https://grafana.com/grafana/download/8.5.14)

Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud) and as always, we closely coordinated with all cloud providers licensed to offer Grafana Pro. They have received early notification under embargo and confirmed that their offerings are secure at the time of this announcement. This is applicable to Amazon Managed Grafana and Azure's Grafana as a service offering.

## Improper authentication - CVE-2022-39229

### Summary 

On September 7 as a result of an internal security audit we have discovered a security vulnerability in Grafana basic authentication, related to the usage of username and email address. 

In Grafana, a user’s username and email address are unique fields, that means no other user can have the same username or email address as another user. 

In addition, a user can have an email address as a username and Grafana login allows users to sign in with either username or email address. This creates an unusual behavior, where _user_1_ can register with one email address and _user_2_ can register their username as _user_1_’s email address. As a result, _user_1_ would be prevented to sign in Grafana, since _user_1_ password won’t match with _users_2_ email address.

The CVSS score for this vulnerability is 4.3 Moderate (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L).

### Impacted versions

All installations for Grafana versions <=9.x, <=8.x

### Solutions and mitigations

To fully address CVE-2022-39229 please upgrade your Grafana instances. 
Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud).

## Reporting security issues

If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

## Security announcements

We maintain a [security category](https://community.grafana.com/c/support/security-announcements) on our blog, where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-gj7m-853r-289r
- https://nvd.nist.gov/vuln/detail/CVE-2022-39229
- https://github.com/grafana/grafana/commit/5644758f0c5ae9955a4e5480d71f9bef57fdce35
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/releases/tag/v9.1.8
