# [C] Argo CD's external URLs for Deployments can include JavaScript

## Summary
Severity: Critical
Advisory: GHSA-h4w9-6x78-8vrj
CVE: CVE-2022-31035
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-h4w9-6x78-8vrj
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=1.0.0 <2.1.16
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.1.16
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.2.0 <2.2.10
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.3.0 <2.3.5
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.4.0 <2.4.1

## Details
### Impact

All unpatched versions of Argo CD starting with v1.0.0 are vulnerable to a cross-site scripting (XSS) bug allowing a malicious user to inject a `javascript:` link in the UI. When clicked by a victim user, the script will execute with the victim's permissions (up to and including admin).

The script would be capable of doing anything which is possible in the UI or via the API, such as creating, modifying, and deleting Kubernetes resources.

### Patches

A patch for this vulnerability has been released in the following Argo CD versions:

* v2.4.1
* v2.3.5
* v2.2.10
* v2.1.16

### Workarounds

There are no completely-safe workarounds besides upgrading.

**Mitigations:**

1. Avoid clicking external links presented in the UI. Here is an example of an Application node with an external link:

   ![Application node in the Argo CD UI with an external link](https://user-images.githubusercontent.com/350466/171678146-026bbf20-2116-4b9f-8af8-7bb5b7ee8dff.png)

   The link's title is user-configurable. So even if you hover the link, and the tooltip looks safe, the link might be malicious. The only way to be certain that the link is safe is to inspect the page's source.

2. Carefully limit who has permissions to edit resource manifests (this is configured in [RBAC](https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/)).

### References

* [Documentation for the external links feature](https://argo-cd.readthedocs.io/en/stable/user-guide/external-url/)

### Credits

Disclosed by ADA Logics in a security audit of the Argo project sponsored by CNCF and facilitated by OSTIF. Thanks to Adam Korczynski and David Korczynski for their work on the audit.

### For more information

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-h4w9-6x78-8vrj
- https://nvd.nist.gov/vuln/detail/CVE-2022-31035
- https://github.com/argoproj/argo-cd/commit/8bc3ef690de29c68a36f473908774346a44d4038
- https://argo-cd.readthedocs.io/en/stable/user-guide/external-url
- https://github.com/argoproj/argo-cd
