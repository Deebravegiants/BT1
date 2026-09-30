# [C] Improper Authorization and Origin Validation Error in OneFuzz

## Summary
Severity: Critical
Advisory: GHSA-q5vh-6whw-x745
CVE: CVE-2021-37705
CWE: CWE-285, CWE-346, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2021-08-13
Source: https://github.com/advisories/GHSA-q5vh-6whw-x745
Type: github-advisory

## Affected
- PyPI: `onefuzz` — affected >=2.12.0 <2.31.0

## Details
## Impact

Starting with OneFuzz 2.12.0 or greater, an incomplete authorization check allows an authenticated user from any Azure Active Directory tenant to make authorized API calls to a vulnerable OneFuzz instance.

To be vulnerable, a OneFuzz deployment must be:
* Version 2.12.0 or greater
* Deployed with the non-default [`--multi_tenant_domain`](https://github.com/microsoft/onefuzz/blob/2.30.0/src/deployment/deploy.py#L1021) option

This can result in read/write access to private data such as:
* Software vulnerability and crash information
* Security testing tools
* Proprietary code and symbols

Via authorized API calls, this also enables tampering with existing data and unauthorized code execution on Azure compute resources.

## Patches

This issue is resolved starting in release 2.31.0, via the addition of application-level check of the bearer token's `issuer` against an administrator-configured allowlist.

## Workarounds

Users can restrict access to the tenant of a deployed OneFuzz instance < 2.31.0 by redeploying in the default configuration, which omits the `--multi_tenant_domain` option.

## References

You can find an overview of the Microsoft Identity Platform [here](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-overview).  This vulnerability applies to the multi-tenant application pattern, as described [here](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-convert-app-to-be-multi-tenant).

## For more information
If you have any questions or comments about this advisory:
* Open an issue in [OneFuzz](https://github.com/microsoft/onefuzz)
* Email us at [fuzzing@microsoft.com](mailto:fuzzing@microsoft.com)

## References
- https://github.com/microsoft/onefuzz/security/advisories/GHSA-q5vh-6whw-x745
- https://nvd.nist.gov/vuln/detail/CVE-2021-37705
- https://github.com/microsoft/onefuzz/pull/1153
- https://github.com/microsoft/onefuzz/commit/2fcb4998887959b4fa11894a068d689189742cb1
- https://github.com/microsoft/onefuzz
- https://github.com/microsoft/onefuzz/releases/tag/2.31.0
- https://github.com/pypa/advisory-database/tree/main/vulns/onefuzz/PYSEC-2021-344.yaml
- https://pypi.org/project/onefuzz
