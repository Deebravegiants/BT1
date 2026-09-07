# [C] Argo CD allows cross-site scripting on repositories page

## Summary
Severity: Critical
Advisory: GHSA-2hj5-g64g-fp6p
CVE: CVE-2025-47933
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-2hj5-g64g-fp6p
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=1.2.0-rc1
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.0.0-rc3 <2.13.8
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.14.0-rc1 <2.14.13
- Go: `github.com/argoproj/argo-cd/v3` — affected >=0 <3.0.4

## Details
### Impact
This vulnerability allows an attacker to perform arbitrary actions on behalf of the victim via the API, such as creating, modifying, and deleting Kubernetes resources. Due to the improper filtering of URL protocols in the repository page, an attacker can achieve cross-site scripting with permission to edit the repository.

In `ui/src/app/shared/components/urls.ts`, the following code exists to parse the repository URL.

https://github.com/argoproj/argo-cd/blob/0ae5882d5ae9fe88efc51f65ca8543fb8c3a0aa1/ui/src/app/shared/components/urls.ts#L14-L26

Since this code doesn't validate the protocol of repository URLs, it's possible to inject `javascript:` URLs here.

https://github.com/argoproj/argo-cd/blob/0ae5882d5ae9fe88efc51f65ca8543fb8c3a0aa1/ui/src/app/shared/components/repo.tsx#L5-L7

As the return value of this function is used in the `href` attribute of the `a` tag, it's possible to achieve cross-site scripting by using `javascript:` URLs.

Browsers may return the proper hostname for `javascript:` URLs, allowing exploitation of this vulnerability.

### Patches
A patch for this vulnerability has been released in the following Argo CD versions:
- v3.0.4
- v2.14.13
- v2.13.8


The patch incorporates a way to validate the URL being passed in. Returning `null` if the validation fails.

### Workarounds
There are no workarounds other than depending on the browser to filter the URL. 

### Credits
Disclosed by @Ry0taK [RyotaK](https://ryotak.net). 

### For more information
Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-2hj5-g64g-fp6p
- https://nvd.nist.gov/vuln/detail/CVE-2025-47933
- https://github.com/argoproj/argo-cd/commit/a5b4041a79c54bc7b3d090805d070bcdb9a9e4d1
- https://github.com/argoproj/argo-cd
