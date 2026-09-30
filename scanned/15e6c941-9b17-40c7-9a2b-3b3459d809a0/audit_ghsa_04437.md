# [M] OpenStack Ironic: Crafted JSON String to Certain Endpoints on the API or JSON-RPC Service May Result in Service Crash

## Summary
Severity: Medium
Advisory: GHSA-q3g8-rjrx-59ph
CVE: CVE-2026-50589
CWE: CWE-502, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-q3g8-rjrx-59ph
Type: github-advisory

## Affected
- PyPI: `ironic` — affected >=32.0.0 <37.0.0

## Details
In OpenStack Ironic 32.0.0 through 35.0.1, an unauthenticated malicious user could submit a crafted JSON string to some endpoints on the API or JSON-RPC service and effect a service crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50589
- https://access.redhat.com/security/cve/CVE-2026-50589
- https://bugs.launchpad.net/ironic/+bug/2154288
- https://bugzilla.redhat.com/show_bug.cgi?id=2485353
- https://github.com/openstack/ironic
- https://github.com/pypa/advisory-database/tree/main/vulns/ironic/PYSEC-2026-216.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-50589.json
- https://wiki.openstack.org/wiki/OSSN/OSSN-0099
- http://www.openwall.com/lists/oss-security/2026/06/06/2
