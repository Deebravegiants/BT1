# [M] CVE-2021-4158

## Summary
Severity: Medium
Advisory: CVE-2021-4158
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-4158
Type: osv

## Details
A NULL pointer dereference issue was found in the ACPI code of QEMU. A malicious, privileged user within the guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service condition.

## References
- https://access.redhat.com/security/cve/CVE-2021-4158
- https://bugzilla.redhat.com/show_bug.cgi?id=2035002
- https://gitlab.com/qemu-project/qemu/-/commit/9bd6565ccee68f72d5012e24646e12a1c662827e
- https://www.mail-archive.com/qemu-devel%40nongnu.org/msg857944.html
- https://gitlab.com/qemu-project/qemu/-/issues/770
