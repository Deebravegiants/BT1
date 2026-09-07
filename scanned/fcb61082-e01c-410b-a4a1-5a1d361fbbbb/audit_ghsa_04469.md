# [M] OpenFGA: OIDC audience validation skipped when --authn-oidc-audience is unset

## Summary
Severity: Medium
Advisory: GHSA-hcxc-wf8j-23hv
CVE: CVE-2026-55689
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-hcxc-wf8j-23hv
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <1.18.0

## Details
## Description

OpenFGA's OIDC authenticator skipped JWT audience (`aud`) validation when no audience was configured.
In deployments where one identity provider issues tokens for multiple services,
a token minted for an unrelated service could authenticate to OpenFGA.

## Preconditions

This applies if the following preconditions are met:

1. You run OpenFGA with `authn.method` set to `oidc`.
2. You configured `authn.oidc.issuer` but did **not** set
   `authn.oidc.audience` (`--authn-oidc-audience` / `OPENFGA_AUTHN_OIDC_AUDIENCE`).

## Fix

Upgrade to OpenFGA 1.18.0 or greater. OpenFGA now refuses to start in `oidc`
mode unless both `authn.oidc.issuer` and `authn.oidc.audience` are set, and the
`aud` claim is always validated.

## Acknowledgements

OpenFGA would like to thank https://github.com/0xVijay for the report.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-hcxc-wf8j-23hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-55689
- https://github.com/openfga/openfga/commit/44596773b2e62738720ef215bf7fa04352954271
- https://github.com/openfga/helm-ch
- https://github.com/openfga/helm-charts/releases/tag/openfga-0.3.9
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v1.18.0
