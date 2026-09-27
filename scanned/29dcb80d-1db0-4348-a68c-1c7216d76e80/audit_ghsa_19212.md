# [C] LTI JupyterHub Authenticator does not properly validate JWT Signature

## Summary
Severity: Critical
Advisory: GHSA-mcgx-2gcr-p3hp
CVE: CVE-2023-25574
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-25
Source: https://github.com/advisories/GHSA-mcgx-2gcr-p3hp
Type: github-advisory

## Affected
- PyPI: `jupyterhub-ltiauthenticator` — affected >=1.3.0 <1.4.0

## Details
### Impact

Only users that has configured a JupyterHub installation to use the authenticator class `LTI13Authenticator` are influenced.

LTI13Authenticator that was introduced in `jupyterhub-ltiauthenticator` 1.3.0 wasn't validating JWT signatures. This is believed to allow the LTI13Authenticator to authorize a forged request granting access to existing and new user identities.

### Patches

None.

### Workarounds

None.

### References

- [This code segment](https://github.com/jupyterhub/ltiauthenticator/blob/3feec2e81b9d3b0ad6b58ab4226af640833039f3/ltiauthenticator/lti13/validator.py#L122-L164) didn't validate a JWT signature.

## References
- https://github.com/jupyterhub/ltiauthenticator/security/advisories/GHSA-mcgx-2gcr-p3hp
- https://nvd.nist.gov/vuln/detail/CVE-2023-25574
- https://github.com/jupyterhub/ltiauthenticator
- https://github.com/jupyterhub/ltiauthenticator/blob/3feec2e81b9d3b0ad6b58ab4226af640833039f3/ltiauthenticator/lti13/validator.py#L122-L164
- https://github.com/jupyterhub/ltiauthenticator/blob/main/CHANGELOG.md#140---2023-03-01
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterhub-ltiauthenticator/PYSEC-2025-120.yaml
