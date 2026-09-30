# [M] Openstack Octavia Access Control Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jjgh-m322-fjx6
CVE: CVE-2019-3895
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jjgh-m322-fjx6
Type: github-advisory

## Affected
- PyPI: `octavia` — affected >=0 <0.9.0

## Details
### Description
An access-control flaw was found in the Octavia service when the cloud platform was deployed using Red Hat OpenStack Platform Director. An attacker could cause new amphorae to run based on any arbitrary image. This meant that a remote attacker could upload a new amphorae image and, if requested to spawn new amphorae, Octavia would then pick up the compromised image.

### Mitigation
To prevent this vulnerability:
1. Update Octavia's configuration setting (octavia.conf) to `amp_image_owner_id = $UUID_OF_SERVICE_PROJECT` on all Octavia nodes.
2. Enable the new configuration by restarting both `octavia_worker` and `octavia_health_manager`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3895
- https://github.com/openstack/octavia/commit/d7d062a47ab54a540d81f13a0e5f3085ebfaa0d2
- https://github.com/openstack/tripleo-common/commit/e7c5eab712e0f70ecbc6d225d4766e0fe0f3f884
- https://access.redhat.com/errata/RHSA-2019:1683
- https://access.redhat.com/errata/RHSA-2019:1742
- https://bugs.launchpad.net/octavia/+bug/1620629
- https://bugs.launchpad.net/tripleo/+bug/1830607
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3895
- https://github.com/openstack/octavia
- https://github.com/openstack/octavia/blob/08570831754d9671fbd1756d668f55f191e47ca4/octavia/compute/drivers/nova_driver.py#L35
- https://github.com/pypa/advisory-database/tree/main/vulns/octavia/PYSEC-2019-194.yaml
- https://opendev.org/openstack/octavia/commit/d7d062a47ab54a540d81f13a0e5f3085ebfaa0d2
