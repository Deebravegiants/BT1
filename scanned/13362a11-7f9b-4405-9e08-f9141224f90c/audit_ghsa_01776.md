# [H] Improper Access Control in novajoin

## Summary
Severity: High
Advisory: GHSA-xf8c-3cgx-fcwm
CVE: CVE-2019-10138
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-03-12
Source: https://github.com/advisories/GHSA-xf8c-3cgx-fcwm
Type: github-advisory

## Affected
- PyPI: `novajoin` — affected >=0 <1.1.1

## Details
A flaw was discovered in the python-novajoin plugin, all versions up to, excluding 1.1.1, for Red Hat OpenStack Platform. The novajoin API lacked sufficient access control, allowing any keystone authenticated user to generate FreeIPA tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10138
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10138
- https://github.com/openstack-archive/novajoin
- https://github.com/pypa/advisory-database/tree/main/vulns/novajoin/PYSEC-2019-192.yaml
- https://review.opendev.org/#/c/631240
