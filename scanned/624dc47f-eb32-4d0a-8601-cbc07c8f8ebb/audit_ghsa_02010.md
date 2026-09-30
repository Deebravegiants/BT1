# [M] Improper Neutralization of Special Elements in Output in helm.sh/helm/v3

## Summary
Severity: Medium
Advisory: GHSA-c38g-469g-cmgx
CVE: CVE-2021-21303
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-c38g-469g-cmgx
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=3.0.0 <3.5.2

## Details
Since Helm 2 was released, a well-documented aspect of Helm is that the Helm chart's version number MUST follow the SemVer2 specification. In the past, Helm would not permit charts with malformed versions. At some point, a patch was merged that changed this - On a version parse error, the version number was simply passed along as-is. This provided a vector for malicious data to be injected into Helm and potentially used in various ways.

Core maintainers were able to send deceptive information to a terminal screen running the `helm` command, as well as obscure or alter information on the screen. In some cases, we could send codes that terminals used to execute higher-order logic, like clearing a terminal screen.

Further, during evaluation, the Helm maintainers discovered a few other fields that were not properly sanitized when read out of repository index files. This fix remedies all such cases, and once again enforces SemVer2 policies on version fields.

All users of the Helm 3 should upgrade.

Those who use Helm as a library should verify that they either sanitize this data on their own, or use the proper Helm API calls to sanitize the data.

### Patches
This issue has been resolved in Helm 3.5.2.

While this fix does not constitute a breaking change, as all field formatting is now enforced as documented, it is possible that charts that were mistakenly allowed (but invalid) may no longer be available in search indexes. Specifically, **malformed SemVer versions are no longer supported**. This has always been the documented case, but it is true that malformed versions were allowed.

Note that this is the first security release since Helm 2's final deprecation. Helm 2 was not audited for vulnerability to this issue, and should be assumed vulnerable.

## References
- https://github.com/helm/helm/security/advisories/GHSA-c38g-469g-cmgx
- https://nvd.nist.gov/vuln/detail/CVE-2021-21303
- https://github.com/helm/helm/commit/6ce9ba60b73013857e2e7c73d3f86ed70bc1ac9a
- https://github.com/advisories/GHSA-c38g-469g-cmgx
- https://github.com/helm/helm
- https://github.com/helm/helm/releases/tag/v3.5.2
- https://pkg.go.dev/vuln/GO-2022-1040
