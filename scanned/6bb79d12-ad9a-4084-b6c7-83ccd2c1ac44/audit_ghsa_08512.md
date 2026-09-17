# [M] OpenStack Keystone has an Incorrect Authorization issue

## Summary
Severity: Medium
Advisory: GHSA-q623-f4j4-p4xj
CVE: CVE-2026-43000
CWE: CWE-266, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-q623-f4j4-p4xj
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=14.0.0 <27.0.2
- PyPI: `keystone` — affected >=28.0.0 <28.0.2
- PyPI: `keystone` — affected >=29.0.0 <29.0.2

## Details
An issue was discovered in OpenStack Keystone before 29.0.2. When combined with an application credential impersonation vulnerability, an attacker with the member role on a project can escalate to admin by chaining unrestricted application credentials with Keystone trusts. The impersonated token carries the victim's identity, which passes the trustor validation check. Keystone then validates the delegated roles against the victim's actual role assignments in the database, not the roles on the requesting token. This allows the attacker to create a trust delegating the victim's admin role to themselves. The trust persists independently, and additional trusts and application credentials can be created to maintain access. All actions are logged under the victim's identity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43000
- https://access.redhat.com/security/cve/CVE-2026-43000
- https://bugs.launchpad.net/keystone/+bug/2148477
- https://bugzilla.redhat.com/show_bug.cgi?id=2482826
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2026-601.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43000.json
- https://security.openstack.org/ossa/OSSA-2026-015.html
