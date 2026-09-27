# [H] OpenStack Kolla sudo privilege escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-rvxr-pf5f-j2qj
CVE: CVE-2022-38060
CWE: CWE-269, CWE-426
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-rvxr-pf5f-j2qj
Type: github-advisory

## Affected
- PyPI: `kolla` — affected >=0 <15.0.0.0rc1

## Details
A privilege escalation vulnerability exists in the sudo functionality of OpenStack Kolla git master 05194e7618. A misconfiguration in /etc/sudoers within a container can lead to increased privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38060
- https://github.com/openstack/kolla/commit/2a4a8fce31c12114e8f472c24dd96864b5bd2bd2
- https://bugs.launchpad.net/kolla/+bug/1985784
- https://bugzilla.redhat.com/show_bug.cgi?id=2124758
- https://github.com/openstack/kolla
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1589
