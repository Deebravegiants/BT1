# [C] Injection vulnerability that affects ironic-discoverd

## Summary
Severity: Critical
Advisory: GHSA-x64g-wjmw-w328
CVE: CVE-2015-5306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-x64g-wjmw-w328
Type: github-advisory

## Affected
- PyPI: `python-ironic-inspector-client` — affected >=0 <0.2.5
- PyPI: `ironic-inspector` — affected >=0 <2.2.2

## Details
OpenStack Ironic Inspector (aka ironic-inspector or ironic-discoverd), when debug mode is enabled, might allow remote attackers to access the Flask console and execute arbitrary Python code by triggering an error.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5306
- https://access.redhat.com/errata/RHSA-2015:1929
- https://access.redhat.com/errata/RHSA-2015:2685
- https://access.redhat.com/security/cve/CVE-2015-5306
- https://bugs.launchpad.net/ironic-inspector/+bug/1506419
- https://bugzilla.redhat.com/show_bug.cgi?id=1273698
- https://github.com/pypa/advisory-database/tree/main/vulns/ironic-inspector/PYSEC-2015-28.yaml
- https://opendev.org/openstack/ironic-inspector
- https://opendev.org/openstack/ironic-inspector/commit/2c64da2bee6eeea27c08eb7a94894feaa5494910
- https://opendev.org/openstack/ironic-inspector/commit/77d0052c5133034490386fbfadfdb1bdb49aa44f
- http://rhn.redhat.com/errata/RHSA-2015-2685.html
