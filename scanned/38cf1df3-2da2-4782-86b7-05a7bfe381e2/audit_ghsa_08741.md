# [M] OpenStack Keystone doesn't verify that the user supplied in the authentication request matches the owner of the application credential

## Summary
Severity: Medium
Advisory: GHSA-8f8m-wrvr-wcvf
CVE: CVE-2026-42998
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-8f8m-wrvr-wcvf
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=14.0.0 <27.0.2
- PyPI: `keystone` — affected >=28.0.0 <28.0.2
- PyPI: `keystone` — affected >=29.0.0 <29.0.2

## Details
An issue was discovered in OpenStack Keystone before 29.0.2. The Keystone application credential authentication plugin does not verify that the user supplied in the authentication request matches the owner of the application credential. An attacker can authenticate with their own application credential ID and secret while specifying a different user's name and domain in the request body. Keystone issues a token attributed to the victim user. The impersonated token is project-scoped and carries the intersection of the application credential's roles and the victim's actual roles on the project. This enables audit evasion, reading the victim's credentials, and acting as the victim within shared projects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42998
- https://bugs.launchpad.net/keystone/+bug/2148477
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2026-599.yaml
- https://security.openstack.org/ossa/OSSA-2026-015.html
