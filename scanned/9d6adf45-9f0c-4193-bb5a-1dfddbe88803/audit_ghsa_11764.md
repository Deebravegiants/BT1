# [H] Juju has unauthorized update of out-of-scope Vault secrets

## Summary
Severity: High
Advisory: GHSA-89x7-5m5m-mcmm
CVE: CVE-2026-32692
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-89x7-5m5m-mcmm
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0.0.0-20230919230135-f6a66aa91eec <0.0.0-20260319091847-d06919eb03ec

## Details
An authorization bypass vulnerability in the Vault secrets back-end implementation of Juju versions 3.1.6 through 3.6.18 allows an authenticated unit agent to perform unauthorized updates to secret revisions. With sufficient information, an attacker can poison any existing secret revision within the scope of that Vault secret back-end.


### Impact
An authenticated unit agent can update any secret revision of a Vault back-end
that the unit's model uses. With sufficient information, an attacker can poison
any existing secret revision within the scope of that Vault secret back-end.

### Patches
3.6.19

## References
- https://github.com/juju/juju/security/advisories/GHSA-89x7-5m5m-mcmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32692
- https://github.com/juju/juju/commit/d06919eb03ec68156818bcc304b5fe1c39a8f9e9
- https://github.com/juju/juju
