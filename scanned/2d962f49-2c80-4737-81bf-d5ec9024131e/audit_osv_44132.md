# [H] CVE-2026-80184

## Summary
Severity: High
Advisory: CVE-2026-80184
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80184
Type: osv

## Details
In OpenStack Keystone before 29.0.3, tokens obtained via delegated authentication mechanisms (OAuth1 access tokens, application credentials, trusts) could be submitted to the token-method authentication path for reauthentication to escape their intended project scope. When an application credential token was presented with no explicit scope, Keystone would issue a new token scoped to the credential owner's default project rather than the project for which the credential was issued, bypassing the intended project boundary. All Keystone deployments that permit delegated authentication through OAuth1 access tokens, application credentials, or trusts are affected.

## References
- https://opendev.org/openstack/keystone
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80184.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80184
- https://security.openstack.org/ossa/OSSA-2026-037.html
- https://www.openwall.com/lists/oss-security/2026/08/25/5
- https://launchpad.net/bugs/2158538
- https://bugs.launchpad.net/keystone/+bug/2158538
