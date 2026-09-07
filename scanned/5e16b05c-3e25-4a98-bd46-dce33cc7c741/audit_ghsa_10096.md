# [H] OpenStack Keystone: LDAP identity backend does not convert enabled attribute to boolean

## Summary
Severity: High
Advisory: GHSA-pfx2-9x9m-7ghx
CVE: CVE-2026-40683
CWE: CWE-843
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-pfx2-9x9m-7ghx
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <28.0.1

## Details
In OpenStack Keystone before 28.0.1, the LDAP identity backend does not convert the user enabled attribute to a boolean when the user_enabled_invert configuration option is False (the default). The _ldap_res_to_model method in the UserApi class only performed string-to-boolean conversion when user_enabled_invert was True. When False, the raw string value from LDAP (e.g., "FALSE") was used directly. Since non-empty strings are truthy in Python, users marked as disabled in LDAP were treated as enabled by Keystone, allowing them to authenticate and perform actions. All deployments using the LDAP identity backend without user_enabled_invert=True or user_enabled_emulation are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40683
- https://bugs.launchpad.net/keystone/+bug/2121152
- https://bugs.launchpad.net/keystone/+bug/2141713
- https://github.com/openstack/keystone
- https://review.opendev.org/958205
- https://www.openwall.com/lists/oss-security/2026/04/14/9
