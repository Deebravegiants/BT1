# [M] Harbor: LDAP password and OIDC secret are not redacted in the audit log

## Summary
Severity: Medium
Advisory: GHSA-prh4-vhfh-24mj
CWE: CWE-312, CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-prh4-vhfh-24mj
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=2.13.0 <2.13.5
- Go: `github.com/goharbor/harbor` — affected >=2.14.0 <2.14.3

## Details
### Impact
Harbor write configuration payload to audit log when configuration change, the ldap_search_password and oidc_client_secret will be logged in the audit log without redacted

### Patches
Harbor v2.15.0, v2.14.3, v2.13.5

### Workarounds
Disable audit log configure event in Harbor Web Console: Go to Administration -> Configuration -> Enable Audit Log Event Type -> Uncheck "Update Configuration" and click "Save" Button.

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-prh4-vhfh-24mj
- https://github.com/goharbor/harbor/commit/85e756486fc19333c5c300d7ac273e1580dc9350
- https://github.com/goharbor/harbor
