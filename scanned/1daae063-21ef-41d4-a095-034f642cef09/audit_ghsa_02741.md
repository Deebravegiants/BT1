# [H] Argo CD Insecure default administrative password

## Summary
Severity: High
Advisory: GHSA-h8jc-jmrf-9h8f
CVE: CVE-2020-8828
CWE: CWE-1188, CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-h8jc-jmrf-9h8f
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=0

## Details
In Argo CD versions 1.8.0 and prior, the default admin password is set to the argocd-server pod name. For insiders with access to the cluster or logs, this issue could be abused for privilege escalation, as Argo has privileged roles. A malicious insider is the most realistic threat, but pod names are not meant to be kept secret and could wind up just about anywhere.

#### Workaround:

The recommended mitigation as described in the user documentation is to use SSO integration. The default admin password should only be used for initial configuration and then [disabled](https://argo-cd.readthedocs.io/en/stable/operator-manual/user-management/#disable-admin-user) or at least changed to a more secure password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8828
- https://argo-cd.readthedocs.io/en/stable/security_considerations/#cve-2020-8828-insecure-default-administrative-password
- https://argoproj.github.io/argo-cd/security_considerations
- https://github.com/argoproj/argo-cd
- https://github.com/argoproj/argo-cd/blob/129cf5370f9e2c6f99c9a5515099250a7ba42099/docs/security_considerations.md#cve-2020-8828---insecure-default-administrative-password
- https://github.com/argoproj/argo/releases
- https://www.soluble.ai/blog/argo-cves-2020
