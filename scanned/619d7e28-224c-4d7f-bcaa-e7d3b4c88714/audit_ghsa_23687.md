# [M] OpenStack Neutron Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hvxr-2fvv-c3wq
CVE: CVE-2017-7543
CWE: CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hvxr-2fvv-c3wq
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=0 <7.2.0-12.1
- PyPI: `neutron` — affected >=8.0.0 <8.3.0-11.1
- PyPI: `neutron` — affected >=9.0.0 <9.3.1-2.1
- PyPI: `neutron` — affected >=10.0.0 <10.0.2-1.1

## Details
A race-condition flaw was discovered in openstack-neutron before 7.2.0-12.1, 8.x before 8.3.0-11.1, 9.x before 9.3.1-2.1, and 10.x before 10.0.2-1.1, where, following a minor overcloud update, neutron security groups were disabled. Specifically, the following were reset to 0: net.bridge.bridge-nf-call-ip6tables and net.bridge.bridge-nf-call-iptables. The race was only triggered by an update, at which point an attacker could access exposed tenant VMs and network resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7543
- https://access.redhat.com/errata/RHSA-2017:2447
- https://access.redhat.com/errata/RHSA-2017:2448
- https://access.redhat.com/errata/RHSA-2017:2449
- https://access.redhat.com/errata/RHSA-2017:2450
- https://access.redhat.com/errata/RHSA-2017:2451
- https://access.redhat.com/errata/RHSA-2017:2452
- https://access.redhat.com/security/cve/CVE-2017-7543
- https://bugzilla.redhat.com/show_bug.cgi?id=1473792
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7543
- https://opendev.org/openstack/neutron
- https://web.archive.org/web/20200227153412/https://www.securityfocus.com/bid/100237
