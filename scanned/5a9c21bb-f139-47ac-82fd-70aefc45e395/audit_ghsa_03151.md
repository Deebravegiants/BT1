# [M] Possible XSS when using SSO with the CLI in github.com/argoproj/argo-cd/v2

## Summary
Severity: Medium
Advisory: GHSA-qq5v-f4c3-395c
CVE: CVE-2021-23347
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-qq5v-f4c3-395c
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <1.7.13
- Go: `github.com/argoproj/argo-cd/v2` — affected >=1.8.0 <1.8.6

## Details
### Impact

When using SSO with the Argo CD CLI, a malicious SSO provider could have sent specially crafted error message that would result in XSS on the client by means of executing arbitrary JavaScript code.

We believe the exploitation of this vulnerability is only be possible when Argo CD is connected to a compromised/malicious SSO provider.

### Patches

A patch for this vulnerability is available with the v1.8.7 and v1.7.14 releases of Argo CD.

### Workarounds

* Do not use SSO with the CLI when you don't trust your SSO provider


If you have any questions or comments about this advisory:

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel `#argo-cd`

### Credits

The issue was found during static code scanning with CodeQL and fixed by the Argo CD team. While we believed that a rogue SSO provider would pose a severe threat by itself, we fixed it like a regular bug.

The Argo CD team would like to thank Adam Gold of Snyk (https://snyk.io) for stepping up and classifying this correctly as a  security issue and for his help in determining its severity. Also, Snyk kindly reserved and provided the CVE for this vulnerability.

We fully agree with Adam that this bug is a security vulnerability and justifies publishing a SA, to provide our community and users full transparancy.

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-qq5v-f4c3-395c
- https://nvd.nist.gov/vuln/detail/CVE-2021-23347
- https://github.com/argoproj/argo-cd/pull/5563
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMARGOPROJARGOCDCMD-1078291
