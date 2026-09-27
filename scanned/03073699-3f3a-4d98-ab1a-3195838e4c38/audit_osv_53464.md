# [H] CVE-2022-43945

## Summary
Severity: High
Advisory: CVE-2022-43945
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-04
Source: https://osv.dev/vulnerability/CVE-2022-43945
Type: osv

## Details
The Linux kernel NFSD implementation prior to versions 5.19.17 and 6.0.2 are vulnerable to buffer overflow. NFSD tracks the number of pages held by each NFSD thread by combining the receive and send buffers of a remote procedure call (RPC) into a single array of pages. A client can force the send buffer to shrink by sending an RPC message over TCP with garbage data added at the end of the message. The RPC message with garbage data is still correctly formed according to the specification and is passed forward to handlers. Vulnerable code in NFSD is not expecting the oversized request and writes beyond the allocated buffer space. CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H

## References
- http://packetstormsecurity.com/files/171289/Kernel-Live-Patch-Security-Notice-LNS-0092-1.html
- https://security.netapp.com/advisory/ntap-20221215-0006/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f90497a16e434c2211c66e3de8e77b17868382b8
