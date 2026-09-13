# [C] LDAP authentication bypass with empty password

## Summary
Severity: Critical
Advisory: GHSA-5hmm-x8q8-w5jh
CVE: CVE-2020-26214
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-11-06
Source: https://github.com/advisories/GHSA-5hmm-x8q8-w5jh
Type: github-advisory

## Affected
- PyPI: `alerta-server` — affected >=8.0.0 <8.1.0
- PyPI: `alerta-server` — affected >=0 <7.5.7

## Details
### Impact
Users may be able to bypass LDAP authentication if they provide an empty password when Alerta server is configure to use LDAP as the authorization provider.

Only deployments where LDAP servers are configured to allow unauthenticated binds (eg. default on Active Directory) are affected.

### Patches
A fix has been implemented that returns HTTP 401 Unauthorized response for any authentication attempts where the password field is empty. See https://github.com/alerta/alerta/pull/1345

### Workarounds
LDAP administrators can disallow unauthenticated bind requests by clients.

### References
https://tools.ietf.org/html/rfc4513#section-5.1.2
https://pypi.org/project/alerta-server/8.1.0/

### For more information
If you have any questions or comments about this advisory:
* Add a comment to the issue [#1277](https://github.com/alerta/alerta/issues/1277)
* Email us at [admin@alerta.dev](mailto:admin@alerta.dev)

## References
- https://github.com/alerta/alerta/security/advisories/GHSA-5hmm-x8q8-w5jh
- https://nvd.nist.gov/vuln/detail/CVE-2020-26214
- https://github.com/alerta/alerta/issues/1277
- https://github.com/alerta/alerta/pull/1345
- https://github.com/alerta/alerta/commit/2bfa31779a4c9df2fa68fa4d0c5c909698c5ef65
- https://github.com/alerta/alerta
- https://github.com/pypa/advisory-database/tree/main/vulns/alerta-server/PYSEC-2020-159.yaml
- https://pypi.org/project/alerta-server/8.1.0
- https://tools.ietf.org/html/rfc4513#section-5.1.2
