# [H] OpenStack Nova calls qemu-img without format restrictions for resize 

## Summary
Severity: High
Advisory: GHSA-m4f3-qp2w-gwh6
CVE: CVE-2026-24708
CWE: CWE-669
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-m4f3-qp2w-gwh6
Type: github-advisory

## Affected
- PyPI: `Nova` — affected >=32.0.0.0rc1
- PyPI: `Nova` — affected >=31.0.0.0rc1
- PyPI: `Nova` — affected >=0

## Details
An issue was discovered in OpenStack Nova before 30.2.2, 31 before 31.2.1, and 32 before 32.1.1. By writing a malicious QCOW header to a root or ephemeral disk and then triggering a resize, a user may convince Nova's Flat image backend to call qemu-img without a format restriction, resulting in an unsafe image resize operation that could destroy data on the host system. Only compute nodes using the Flat image backend (usually configured with use_cow_images=False) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24708
- https://github.com/openstack/nova/commit/3eba22ff09c81a61750fbb4882e5f1f01a20fdf5
- https://bugs.launchpad.net/nova/+bug/2137507
- https://github.com/openstack/nova
- https://lists.debian.org/debian-lts-announce/2026/02/msg00025.html
- https://www.openwall.com/lists/oss-security/2026/02/17/7
