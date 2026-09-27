# [M] Login screen allows message spoofing if SSO is enabled

## Summary
Severity: Medium
Advisory: GHSA-xmg8-99r8-jc2j
CVE: CVE-2022-24905
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xmg8-99r8-jc2j
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.3.0 <2.3.4
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.2.0 <2.2.9
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.0.0 <2.1.15
- Go: `github.com/argoproj/argo-cd` — affected >=0 <2.1.15

## Details
### Impact

A vulnerability was found in Argo CD that allows an attacker to spoof error messages on the login screen when SSO is enabled.

In order to exploit this vulnerability, an attacker would have to trick the victim to visit a specially crafted URL which contains the message to be displayed.

As far as the research of the Argo CD team concluded, it is not possible to specify any active content (e.g. Javascript) or other HTML fragments (e.g. clickable links) in the spoofed message.

### Patched versions

A patch for this vulnerability has been released in the following Argo CD versions:

* v2.3.4
* v2.2.9
* v2.1.15

### Workarounds

No workaround available.

#### Mitigations

It is advised to update to an Argo CD version containing a fix for this issue (see *Patched versions* above).

### Credits

This vulnerability was discovered by Naufal Septiadi (<naufal@horangi.com>) and reported to us in a responsible way. 

### For more information

<!-- Use only one of the paragraphs below. Remove all others. -->

<!-- For Argo CD -->

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-xmg8-99r8-jc2j
- https://nvd.nist.gov/vuln/detail/CVE-2022-24905
- https://github.com/argoproj/argo-cd/releases/tag/v2.1.15
- https://github.com/argoproj/argo-cd/releases/tag/v2.2.9
- https://github.com/argoproj/argo-cd/releases/tag/v2.3.4
- github.com/argoproj/argo-cd
