# [H] CVE-2021-4204

## Summary
Severity: High
Advisory: CVE-2021-4204
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-4204
Type: osv

## Details
An out-of-bounds (OOB) memory access flaw was found in the Linux kernel's eBPF due to an Improper Input Validation. This flaw allows a local attacker with a special privilege to crash the system or leak internal information.

## References
- https://security-tracker.debian.org/tracker/CVE-2021-4204
- https://security.netapp.com/advisory/ntap-20221228-0003/
- https://access.redhat.com/security/cve/CVE-2021-4204
- https://bugzilla.redhat.com/show_bug.cgi?id=2039178
- https://www.openwall.com/lists/oss-security/2022/01/11/4
