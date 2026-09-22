# [H] CVE-2022-2961

## Summary
Severity: High
Advisory: CVE-2022-2961
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-2961
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s PLP Rose functionality in the way a user triggers a race condition by calling bind while simultaneously triggering the rose_bind() function. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://security.netapp.com/advisory/ntap-20230214-0004/
- https://access.redhat.com/security/cve/CVE-2022-2961
