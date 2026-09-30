# [C] CVE-2016-6658

## Summary
Severity: Critical
Advisory: CVE-2016-6658
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2018-03-29
Source: https://osv.dev/vulnerability/CVE-2016-6658
Type: osv

## Details
Applications in cf-release before 245 can be configured and pushed with a user-provided custom buildpack using a URL pointing to the buildpack. Although it is not recommended, a user can specify a credential in the URL (basic auth or OAuth) to access the buildpack through the CLI. For example, the user could include a GitHub username and password in the URL to access a private repo. Because the URL to access the buildpack is stored unencrypted, an operator with privileged access to the Cloud Controller database could view these credentials.

## References
- https://pivotal.io/security/cve-2016-6658
