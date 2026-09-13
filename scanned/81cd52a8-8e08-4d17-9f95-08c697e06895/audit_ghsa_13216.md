# [M] Path traversal allows leaking out-of-bound Helm charts from Argo CD repo-server

## Summary
Severity: Medium
Advisory: GHSA-6jqw-jwf5-rp8h
CVE: CVE-2023-40026
CWE: CWE-22, CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-6jqw-jwf5-rp8h
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=0
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.3.0

## Details
### Impact
In Argo CD versions prior to 2.3 (starting at least in v0.1.0, but likely in any version using Helm before 2.3), using a specifically-crafted Helm file could reference external Helm charts handled by the same repo-server to leak values, or files from the referenced Helm Chart. This was possible because Helm paths were predictable. 

The vulnerability worked by adding a Helm chart that referenced Helm resources from predictable paths. Because the paths of Helm charts were predictable and available on an instance of repo-server, it was possible to reference and then render the values and resources from other existing Helm charts regardless of permissions. While generally, secrets are not stored in these files, it was nevertheless possible to reference any values from these charts. 

### Patches
This issue was fixed in Argo CD 2.3 and subsequent versions by randomizing Helm paths.

### Workarounds
User's still using Argo CD 2.3 or below are advised to update to a [supported version](https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/#supported-versions). If this is not possible, disabling Helm chart rendering, or using an additional repo-server for each Helm chart would prevent possible exploitation.  

### References
https://github.com/argoproj/argo-cd/security/advisories/GHSA-63qx-x74g-jcr7

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [example link to repo](http://example.com)
* Email us at [example email address](mailto:example@example.com)

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-63qx-x74g-jcr7
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-6jqw-jwf5-rp8h
- https://nvd.nist.gov/vuln/detail/CVE-2023-40026
- https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/#supported-versions
- https://github.com/argoproj/argo-cd
