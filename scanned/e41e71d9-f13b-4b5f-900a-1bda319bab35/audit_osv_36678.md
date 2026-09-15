# [H] TensorFlow HDF5 Library Uncontrolled Search Path Element Local Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-2492
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-2492
Type: osv

## Details
TensorFlow HDF5 Library Uncontrolled Search Path Element Local Privilege Escalation Vulnerability. This vulnerability allows local attackers to escalate privileges on affected installations of TensorFlow. An attacker must first obtain the ability to execute low-privileged code on the target system in order to exploit this vulnerability.

The specific flaw exists within the handling of plugins. The application loads plugins from an unsecured location. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of a target user. Was ZDI-CAN-25480.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2492.json
- https://access.redhat.com/errata/RHSA-2026:10184
- https://access.redhat.com/security/cve/CVE-2026-2492
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2492.json
- https://github.com/tensorflow/tensorflow/commit/46e7f7fb144fd11cf6d17c23dd47620328d77082
- https://nvd.nist.gov/vuln/detail/CVE-2026-2492
- https://www.zerodayinitiative.com/advisories/ZDI-26-116/
- https://bugzilla.redhat.com/show_bug.cgi?id=2441510
