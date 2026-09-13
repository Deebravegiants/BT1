# [H] OpenStack Ironic Python Agent Includes Functionality from Untrusted Control Sphere

## Summary
Severity: High
Advisory: GHSA-rmxr-45gj-889w
CVE: CVE-2026-43003
CWE: CWE-78, CWE-829
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-01
Source: https://github.com/advisories/GHSA-rmxr-45gj-889w
Type: github-advisory

## Affected
- PyPI: `ironic-python-agent` — affected >=1.0.0 <11.6.0

## Details
An issue was discovered in OpenStack ironic-python-agent 1.0.0 through 11.5.0. Ironic Python Agent (IPA) sometimes executes grub-install from within a chroot of the deployed partition image, leading to code execution in the case of a malicious image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43003
- https://access.redhat.com/errata/RHSA-2026:51038
- https://access.redhat.com/errata/RHSA-2026:57801
- https://access.redhat.com/errata/RHSA-2026:60446
- https://access.redhat.com/errata/RHSA-2026:60454
- https://access.redhat.com/security/cve/CVE-2026-43003
- https://bugs.launchpad.net/ironic-python-agent/+bug/2148310
- https://bugzilla.redhat.com/show_bug.cgi?id=2464306
- https://github.com/openstack/ironic-python-agent
- https://github.com/openstack/ironic-python-agent/blob/236b33abffe6688afc39c21e351cc3889b3db2dd/ironic_python_agent/efi_utils.py#L134-L139
- https://github.com/pypa/advisory-database/tree/main/vulns/ironic-python-agent/PYSEC-2026-205.yaml
- https://opendev.org/openstack/ironic-python-agent/commit/6cd463a657edcddf7b79416ac69bdef5b6f30099
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43003.json
- http://www.openwall.com/lists/oss-security/2026/06/16/11
