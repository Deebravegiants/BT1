# [H] CVE-2026-80182

## Summary
Severity: High
Advisory: CVE-2026-80182
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80182
Type: osv

## Details
In OpenStack Keystone before 29.0.3, tokens obtained via OAuth1 access token, application credential, or trust-scoped authentication could create new long-lived credentials or authorize new delegations that persist independently of, and outlive, the credential used to obtain them. The delegation restrictions that block these operations did not consistently apply to all delegated token types, allowing an OAuth1-scoped token, for example, to create application credentials or authorize OAuth1 request tokens despite those operations being restricted for other delegated token types. All Keystone deployments that permit delegated authentication through OAuth1 access tokens, application credentials, or trusts are affected.

## References
- https://opendev.org/openstack/keystone
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80182.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80182
- https://security.openstack.org/ossa/OSSA-2026-037.html
- https://www.openwall.com/lists/oss-security/2026/08/25/5
- https://launchpad.net/bugs/2153453
- https://bugs.launchpad.net/keystone/+bug/2153453
