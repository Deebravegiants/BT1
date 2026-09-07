# [H] Prometheus Azure AD remote write OAuth client secret exposed via config API

## Summary
Severity: High
Advisory: GHSA-wg65-39gg-5wfj
CVE: CVE-2026-42151
CWE: CWE-200, CWE-256, CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-wg65-39gg-5wfj
Type: github-advisory

## Affected
- Go: `github.com/prometheus/prometheus` — affected >=0.45.2 <0.311.3

## Details
### Impact

Users who use Azure AD remote write with OAuth authentication are impacted.

The `client_secret` field in the Azure AD remote write OAuth configuration (`storage/remote/azuread`) was typed as `string` instead of `Secret`. Prometheus redacts fields of type `Secret` when serving the configuration via the `/-/config` HTTP API endpoint. Because the field was a plain string, the Azure OAuth client secret was exposed in plaintext to any user or process with access to that endpoint.

### Patches

The problem has been patched by changing `ClientSecret` in `OAuthConfig` to `Secret`. Users should upgrade to 3.11.3 or 3.5.3 LTS.

### Workarounds

Users  who can not upgrade can switch to Managed Identity or Workload Identity authentication for Azure AD remote write, which do not involve a client secret.

## References
- https://github.com/prometheus/prometheus/security/advisories/GHSA-wg65-39gg-5wfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42151
- https://github.com/prometheus/prometheus/pull/18590
- https://github.com/prometheus/prometheus/pull/18587
- https://access.redhat.com/errata/RHSA-2026:60387
- https://access.redhat.com/errata/RHSA-2026:60386
- https://access.redhat.com/errata/RHSA-2026:57191
- https://access.redhat.com/errata/RHSA-2026:56340
- https://access.redhat.com/errata/RHSA-2026:54427
- https://access.redhat.com/errata/RHSA-2026:54288
- https://access.redhat.com/errata/RHSA-2026:53530
- https://access.redhat.com/errata/RHSA-2026:53415
- https://access.redhat.com/errata/RHSA-2026:53413
- https://access.redhat.com/errata/RHSA-2026:53412
- https://access.redhat.com/errata/RHSA-2026:50874
- https://access.redhat.com/errata/RHSA-2026:50843
- https://access.redhat.com/errata/RHSA-2026:25039
- https://access.redhat.com/errata/RHSA-2026:60388
- https://access.redhat.com/errata/RHSA-2026:60389
- https://access.redhat.com/errata/RHSA-2026:60390
