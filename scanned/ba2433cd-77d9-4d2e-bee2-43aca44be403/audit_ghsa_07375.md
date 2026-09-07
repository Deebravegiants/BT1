# [M] core-geonetwork has an Open Redirect Bypass

## Summary
Severity: Medium
Advisory: GHSA-pjp7-q6wp-97qx
CVE: CVE-2026-53573
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-pjp7-q6wp-97qx
Type: github-advisory

## Affected
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=3.12.0
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.0.0-alpha.1
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.2.0 <4.2.16
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.4.0 <4.4.11

## Details
### Summary
GeoNetwork's post-login redirect handling can be bypassed to redirect users to an attacker-controlled external site, even though the code attempts to restrict redirect targets to relative, in-application URLs. This affects both supported SSO login methods: OAuth2/OIDC and Keycloak.

### Details
Both the OAuth2/OIDC and Keycloak login filters validate the client-supplied post-login redirect target before forwarding the browser to it, but the validation does not correctly reject every kind of URL that causes the browser to leave the GeoNetwork origin. As a result, a value that is treated as a safe, in-application relative path by the filter can still cause the browser to be redirected to an external, attacker-controlled host.

### Impact
An attacker can craft a link to a legitimate GeoNetwork OAuth2/OIDC or Keycloak login endpoint that, after the login flow completes, redirects the victim to an arbitrary external site. This can be used for phishing (e.g., presenting a fake login form) or to chain into other attacks hosted externally. This does not bypass authentication or expose GeoNetwork data directly; the impact is Open Redirect (CWE-601).

GeoNetwork 3.x and 4.0.x are archived/unmaintained and will not receive a fix for this issue. Instances running those lines should upgrade to a supported release (4.2.16 or later, or 4.4.11 or later).

## References
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-pjp7-q6wp-97qx
- https://github.com/geonetwork/core-geonetwork/pull/9307
- https://github.com/geonetwork/core-geonetwork/pull/9309
- https://github.com/geonetwork/core-geonetwork/commit/0d74f673dfc926bde935819ed34636d789b2fecd
- https://github.com/geonetwork/core-geonetwork/commit/cde9b6481a29e2473b7b74479b4e3fd6843bac4e
- https://github.com/geonetwork/core-geonetwork
- https://github.com/geonetwork/core-geonetwork/releases/tag/4.2.16
- https://github.com/geonetwork/core-geonetwork/releases/tag/4.4.11
