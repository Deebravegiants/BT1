# [M] CVE-2022-3277

## Summary
Severity: Medium
Advisory: CVE-2022-3277
Aliases: GHSA-w446-h7vg-wv3p, PYSEC-2026-855
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2022-3277
Type: osv

## Details
An uncontrolled resource consumption flaw was found in openstack-neutron. This flaw allows a remote authenticated user to query a list of security groups for an invalid project. This issue creates resources that are unconstrained by the user's quota. If a malicious user were to submit a significant number of requests, this could lead to a denial of service.

## References
- https://bugs.launchpad.net/neutron/+bug/1988026
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3277.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3277
- https://bugzilla.redhat.com/show_bug.cgi?id=2129193
