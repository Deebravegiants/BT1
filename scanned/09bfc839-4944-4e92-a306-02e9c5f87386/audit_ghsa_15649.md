# [M] The Argo CD web terminal session does not handle the revocation of user permissions properly

## Summary
Severity: Medium
Advisory: GHSA-v8wx-v5jq-qhhw
CVE: CVE-2024-41666
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-24
Source: https://github.com/advisories/GHSA-v8wx-v5jq-qhhw
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.6.0 <2.9.21
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.10.0 <2.10.16
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.11.0 <2.11.7

## Details
Argo CD v2.11.3 and before, discovering that even if the user's ```p, role:myrole, exec, create, */*, allow``` permissions are revoked, the user can still send any Websocket message, which allows the user to view sensitive information. Even though they shouldn't have such access.

## Description
Argo CD has a Web-based terminal that allows you to get a shell inside a running pod, just like you would with kubectl exec. However, when the administrator enables this function and grants permission to the user ```p, role:myrole, exec, create, */*, allow```, even if the user revokes this permission, the user can still perform operations in the container, as long as the user keeps the terminal view open for a long time. CVE-2023-40025 Although the token expiration and revocation of the user are fixed, however, the fix does not address the situation of revocation of only user ```p, role:myrole, exec, create, */*, allow``` permissions, which may still lead to the leakage of sensitive information.

### Patches
A patch for this vulnerability has been released in the following Argo CD versions:

v2.11.7
v2.10.16
v2.9.21

### For more information
If you have any questions or comments about this advisory:

Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

### Credits
This vulnerability was found & reported by 
Shengjie Li, Huazhong University of Science and Technology
Zhi Li, Huazhong University of Science and Technology
Weijie Liu, Nankai University

The Argo team would like to thank these contributors for their responsible disclosure and constructive communications during the resolve of this issue

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-v8wx-v5jq-qhhw
- https://nvd.nist.gov/vuln/detail/CVE-2024-41666
- https://github.com/argoproj/argo-cd/commit/05edb2a9ca48f0f10608c1b49fbb0cf7164f6476
- https://github.com/argoproj/argo-cd/commit/e96f32d233504101ddac028a5bf8117433d333d6
- https://github.com/argoproj/argo-cd/commit/ef535230d8bd8ad7b18aab1ea1063e9751d348c4
- https://drive.google.com/file/d/1Fynj5Sho8Lf8CETqsNXZyPKlTDdmgJuN/view?usp=sharing
- https://github.com/argoproj/argo-cd
- https://pkg.go.dev/vuln/GO-2024-3006
