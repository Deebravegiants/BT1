# [M] CVE-2023-28327

## Summary
Severity: Medium
Advisory: CVE-2023-28327
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-28327
Type: osv

## Details
A NULL pointer dereference flaw was found in the UNIX protocol in net/unix/diag.c In unix_diag_get_exact in the Linux Kernel. The newly allocated skb does not have sk, leading to a NULL pointer. This flaw allows a local user to crash or potentially cause a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2177382
