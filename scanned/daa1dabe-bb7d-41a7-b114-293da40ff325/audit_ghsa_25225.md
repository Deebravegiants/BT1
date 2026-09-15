# [H] Openstack ironic-inspector has SQL injection vulnerability in node_cache

## Summary
Severity: High
Advisory: GHSA-c7fc-cm7p-92r2
CVE: CVE-2019-10141
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c7fc-cm7p-92r2
Type: github-advisory

## Affected
- PyPI: `ironic-inspector` — affected >=0 <5.0.2
- PyPI: `ironic-inspector` — affected >=5.1.0 <6.0.3
- PyPI: `ironic-inspector` — affected >=6.1.0 <7.2.4
- PyPI: `ironic-inspector` — affected >=8.0.0 <8.0.3
- PyPI: `ironic-inspector` — affected >=8.1.0 <8.2.1

## Details
A vulnerability was found in openstack-ironic-inspector all versions excluding 5.0.2, 6.0.3, 7.2.4, 8.0.3 and 8.2.1. A SQL-injection vulnerability was found in openstack-ironic-inspector's node_cache.find_node(). This function makes a SQL query using unfiltered data from a server reporting inspection results (by a POST to the /v1/continue endpoint). Because the API is unauthenticated, the flaw could be exploited by an attacker with access to the network on which ironic-inspector is listening. Because of how ironic-inspector uses the query results, it is unlikely that data could be obtained. However, the attacker could pass malicious data and create a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10141
- https://github.com/openstack/ironic-inspector/commit/17c796b49171b6133e988f78c92d7c9b7ed3fcf3
- https://github.com/openstack/ironic-inspector/commit/67ff87ebca1016d44bd9d284ec4c16a88a533cfc
- https://github.com/openstack/ironic-inspector/commit/97f9d34f8376ac7accd2597b3bdce67a9dac664f
- https://github.com/openstack/ironic-inspector/commit/9d107900b2e0b599397b84409580d46e0ed16291
- https://access.redhat.com/errata/RHSA-2019:2505
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10141
- https://docs.openstack.org/releasenotes/ironic-inspector/ocata.html#relnotes-5-0-2-7-origin-stable-ocata
- https://docs.openstack.org/releasenotes/ironic-inspector/pike.html#relnotes-6-0-3-4-stable-pike
- https://docs.openstack.org/releasenotes/ironic-inspector/queens.html#relnotes-7-2-4-stable-queens
- https://docs.openstack.org/releasenotes/ironic-inspector/rocky.html#relnotes-8-0-3-stable-rocky
- https://docs.openstack.org/releasenotes/ironic-inspector/stein.html#relnotes-8-2-1-stable-stein
- https://github.com/openstack/ironic-inspector
- https://github.com/pypa/advisory-database/tree/main/vulns/ironic-inspector/PYSEC-2019-152.yaml
- https://review.opendev.org/c/openstack/ironic-inspector/+/660234
- https://storyboard.openstack.org/#!/story/2005678
