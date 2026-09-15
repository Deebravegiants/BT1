# [H] CVE-2022-4139

## Summary
Severity: High
Advisory: CVE-2022-4139
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-27
Source: https://osv.dev/vulnerability/CVE-2022-4139
Type: osv

## Details
An incorrect TLB flush issue was found in the Linux kernel’s GPU i915 kernel driver, potentially leading to random memory corruption or data leaks. This flaw could allow a local user to crash the system or escalate their privileges on the system.

## References
- https://security.netapp.com/advisory/ntap-20230309-0004/
- https://www.openwall.com/lists/oss-security/2022/11/30/1
- https://bugzilla.redhat.com/show_bug.cgi?id=2147572
