# [M] AAD Pod Identity obtaining token with backslash

## Summary
Severity: Medium
Advisory: GHSA-p82q-rxpm-hjpc
CVE: CVE-2022-23551
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-p82q-rxpm-hjpc
Type: github-advisory

## Affected
- Go: `github.com/Azure/aad-pod-identity` — affected >=0 <1.8.13

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
The [NMI](https://azure.github.io/aad-pod-identity/docs/concepts/nmi/) component in AAD Pod Identity intercepts and validates token requests based on regex. In this case, a token request made with backslash in the request (example: `/metadata/identity\oauth2\token/`) would bypass the NMI validation and be sent to [IMDS](https://learn.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service?tabs=windows) allowing a pod in the cluster to access identities that it shouldn't have access to.

### Patches
_Has the problem been patched? What versions should users upgrade to?_
- We analyzed this bug and determined that we needed to fix it. This fix has been included in AAD Pod Identity release [v1.8.13](https://github.com/Azure/aad-pod-identity/releases/tag/v1.8.13)
- If using the [AKS pod-managed identities add-on](https://learn.microsoft.com/en-us/azure/aks/use-azure-ad-pod-identity), no action is required. The clusters should now be running the `v1.8.13` release.

### For more information

If you have any questions or comments about this advisory:

Open an issue in [Azure/aad-pod-identity](https://github.com/Azure/aad-pod-identity)

## References
- https://github.com/Azure/aad-pod-identity/security/advisories/GHSA-p82q-rxpm-hjpc
- https://nvd.nist.gov/vuln/detail/CVE-2022-23551
- https://github.com/Azure/aad-pod-identity/commit/7e01970391bde6c360d077066ca17d059204cb5d
- https://github.com/Azure/aad-pod-identity
- https://github.com/Azure/aad-pod-identity/releases/tag/v1.8.13
