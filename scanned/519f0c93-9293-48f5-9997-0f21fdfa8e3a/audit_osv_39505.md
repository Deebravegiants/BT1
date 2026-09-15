# [H] rxrpc: Fix potential UAF after skb_unshare() failure

## Summary
Severity: High
Advisory: CVE-2026-45998
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45998
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix potential UAF after skb_unshare() failure

If skb_unshare() fails to unshare a packet due to allocation failure in
rxrpc_input_packet(), the skb pointer in the parent (rxrpc_io_thread())
will be NULL'd out.  This will likely cause the call to
trace_rxrpc_rx_done() to oops.

Fix this by moving the unsharing down to where rxrpc_input_call_event()
calls rxrpc_input_call_packet().  There are a number of places prior to
that where we ignore DATA packets for a variety of reasons (such as the
call already being complete) for which an unshare is then avoided.

And with that, rxrpc_input_packet() doesn't need to take a pointer to the
pointer to the packet, so change that to just a pointer.

## References
- https://git.kernel.org/stable/c/1f2740150f904bfa60e4bad74d65add3ccb5e7f8
- https://git.kernel.org/stable/c/8fde6296c4d4da2be7ab761305ab7f232b94eefd
- https://git.kernel.org/stable/c/996b0487b3cdda4c91811dbb1c9564626bc840bd
- https://git.kernel.org/stable/c/bf20f46d94f1db38e6ffc0ca204a5fe0de01b495
- https://git.kernel.org/stable/c/e3bf143b1e98fb3d6d9e6825bcd683974d478e8c
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45998.json
- https://access.redhat.com/errata/RHSA-2026:34911
- https://access.redhat.com/errata/RHSA-2026:55445
- https://access.redhat.com/errata/RHSA-2026:65708
- https://access.redhat.com/errata/RHSA-2026:65712
- https://access.redhat.com/security/cve/CVE-2026-45998
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45998.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45998
- https://bugzilla.redhat.com/show_bug.cgi?id=2482024
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
