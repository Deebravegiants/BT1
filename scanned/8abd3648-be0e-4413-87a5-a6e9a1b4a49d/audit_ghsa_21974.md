# [H] Access Restriction Bypass in go-ldap

## Summary
Severity: High
Advisory: GHSA-x27w-qxhg-343v
CVE: CVE-2017-14623
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-x27w-qxhg-343v
Type: github-advisory

## Affected
- Go: `github.com/go-ldap/ldap` — affected >=0 <2.5.0

## Details
In the ldap.v2 (aka go-ldap) package through 2.5.0 for Go, an attacker may be able to login with an empty password. This issue affects an application using this package if these conditions are met: (1) it relies only on the return error of the Bind function call to determine whether a user is authorized (i.e., a nil return value is interpreted as successful authorization) and (2) it is used with an LDAP server allowing unauthenticated bind.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14623
- https://github.com/go-ldap/ldap/pull/126
- https://github.com/go-ldap/ldap/commit/95ede1266b237bf8e9aa5dce0b3250e51bfefe66
