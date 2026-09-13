# [H] CVE-2022-1976

## Summary
Severity: High
Advisory: CVE-2022-1976
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-1976
Type: osv

## Details
A flaw was found in the Linux kernel’s implementation of IO-URING. This flaw allows an attacker with local executable permission to create a string of requests that can cause a use-after-free flaw within the kernel. This issue leads to memory corruption and possible privilege escalation.

## References
- https://security.netapp.com/advisory/ntap-20230214-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2092549
