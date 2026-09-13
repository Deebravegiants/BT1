# [H] CVE-2021-47131

## Summary
Severity: High
Advisory: CVE-2021-47131
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47131
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tls: Fix use-after-free after the TLS device goes down and up

When a netdev with active TLS offload goes down, tls_device_down is
called to stop the offload and tear down the TLS context. However, the
socket stays alive, and it still points to the TLS context, which is now
deallocated. If a netdev goes up, while the connection is still active,
and the data flow resumes after a number of TCP retransmissions, it will
lead to a use-after-free of the TLS context.

This commit addresses this bug by keeping the context alive until its
normal destruction, and implements the necessary fallbacks, so that the
connection can resume in software (non-offloaded) kTLS mode.

On the TX side tls_sw_fallback is used to encrypt all packets. The RX
side already has all the necessary fallbacks, because receiving
non-decrypted packets is supported. The thing needed on the RX side is
to block resync requests, which are normally produced after receiving
non-decrypted packets.

The necessary synchronization is implemented for a graceful teardown:
first the fallbacks are deployed, then the driver resources are released
(it used to be possible to have a tls_dev_resync after tls_dev_del).

A new flag called TLS_RX_DEV_DEGRADED is added to indicate the fallback
mode. It's used to skip the RX resync logic completely, as it becomes
useless, and some objects may be released (for example, resync_async,
which is allocated and freed by the driver).

## References
- https://git.kernel.org/stable/c/0f1e6fe66977a864fe850522316f713d7b926fd9
- https://git.kernel.org/stable/c/c55dcdd435aa6c6ad6ccac0a4c636d010ee367a4
- https://git.kernel.org/stable/c/f1d4184f128dede82a59a841658ed40d4e6d3aa2
