# [M] Rancher UI has multiple Cross-Site Scripting (XSS) issues

## Summary
Severity: Medium
Advisory: GHSA-46v3-ggjg-qq3x
CVE: CVE-2022-43760
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-46v3-ggjg-qq3x
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.13
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.7.4

## Details
### Impact
Multiple Cross-Site Scripting (XSS) vulnerabilities have been identified in the Rancher UI. 
Cross-Site scripting allows a malicious user to inject code that is executed within another user's browser, allowing the attacker to steal sensitive information, manipulate web content, or perform other malicious activities on behalf of the victims. This could result in a user with write access to the affected areas being able to act on behalf of an administrator, once an administrator opens the affected web page.

The affected areas include the Projects/Namespaces and Auth Provider sections. The attacker needs to be authenticated and have write access to those features in order to exploit the vulnerabilities. Some of the permissions (roles) required are:

- Project Owner.
- Restricted Admin.
- Configure Authentication.
- Administrator.
- Custom RBAC Role that provides write access on Projects or External Authentication Providers.

For users that suspect this vulnerability may have targeted their Rancher instance, we recommend rotating all API Keys and Kubeconfig tokens.

It's also advised to review logs and possibly rotate credentials stored as secrets in Rancher and downstream cluster, if you believe that users' credentials to access Rancher and its clusters might have been compromised.

### Patches
Patched versions include releases `2.6.13`, `2.7.4` and later versions.

### Workarounds
There is no direct mitigation besides updating Rancher to a patched version.

### Credits
We would like to recognize and thank @bybit-sec for the responsible disclosure of this security issue.

### For more information
If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-46v3-ggjg-qq3x
- https://nvd.nist.gov/vuln/detail/CVE-2022-43760
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2022-43760
- https://github.com/rancher/rancher
- https://github.com/rancher/rancher/releases/tag/v2.6.13
- https://github.com/rancher/rancher/releases/tag/v2.7.4
