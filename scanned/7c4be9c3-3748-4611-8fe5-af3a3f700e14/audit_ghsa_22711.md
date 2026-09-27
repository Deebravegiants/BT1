# [H] OpenStack Mistral DoS

## Summary
Severity: High
Advisory: GHSA-443j-6p7g-6v4w
CVE: CVE-2018-16848
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-443j-6p7g-6v4w
Type: github-advisory

## Affected
- PyPI: `mistral` — affected >=0 <10.0.0

## Details
A Denial of Service (DoS) condition is possible in OpenStack Mistral in versions up to and including 7.0.3. Submitting a specially crafted workflow definition YAML file containing nested anchors can lead to resource exhaustion culminating in a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16848
- https://github.com/openstack/mistral/commit/eac23d9e774f658f9d4743c99aa2743eb104c3f9
- https://bugs.launchpad.net/mistral/+bug/1785657
- https://bugzilla.redhat.com/show_bug.cgi?id=1645332
- https://github.com/openstack/mistral
- https://github.com/pypa/advisory-database/tree/main/vulns/mistral/PYSEC-2020-240.yaml
