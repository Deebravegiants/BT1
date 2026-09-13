# [H] CVE-2022-0435

## Summary
Severity: High
Advisory: CVE-2022-0435
Aliases: A-228560328, PUB-A-228560328
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2022-0435
Type: osv

## Details
A stack overflow flaw was found in the Linux kernel's TIPC protocol functionality in the way a user sends a packet with malicious content where the number of domain member nodes is higher than the 64 allowed. This flaw allows a remote user to crash the system or possibly escalate their privileges if they have access to the TIPC network.

## References
- https://security.netapp.com/advisory/ntap-20220602-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2048738
- https://www.openwall.com/lists/oss-security/2022/02/10/1
