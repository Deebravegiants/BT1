# [M] CVE-2021-47267

## Summary
Severity: Medium
Advisory: CVE-2021-47267
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47267
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: fix various gadget panics on 10gbps cabling

usb_assign_descriptors() is called with 5 parameters,
the last 4 of which are the usb_descriptor_header for:
  full-speed (USB1.1 - 12Mbps [including USB1.0 low-speed @ 1.5Mbps),
  high-speed (USB2.0 - 480Mbps),
  super-speed (USB3.0 - 5Gbps),
  super-speed-plus (USB3.1 - 10Gbps).

The differences between full/high/super-speed descriptors are usually
substantial (due to changes in the maximum usb block size from 64 to 512
to 1024 bytes and other differences in the specs), while the difference
between 5 and 10Gbps descriptors may be as little as nothing
(in many cases the same tuning is simply good enough).

However if a gadget driver calls usb_assign_descriptors() with
a NULL descriptor for super-speed-plus and is then used on a max 10gbps
configuration, the kernel will crash with a null pointer dereference,
when a 10gbps capable device port + cable + host port combination shows up.
(This wouldn't happen if the gadget max-speed was set to 5gbps, but
it of course defaults to the maximum, and there's no real reason to
artificially limit it)

The fix is to simply use the 5gbps descriptor as the 10gbps descriptor,
if a 10gbps descriptor wasn't provided.

Obviously this won't fix the problem if the 5gbps descriptor is also
NULL, but such cases can't be so trivially solved (and any such gadgets
are unlikely to be used with USB3 ports any way).

## References
- https://git.kernel.org/stable/c/45f9a2fe737dc0a5df270787f2231aee8985cd59
- https://git.kernel.org/stable/c/5ef23506695b01d5d56a13a092a97f2478069d75
- https://git.kernel.org/stable/c/70cd19cb5bd94bbb5bacfc9c1e4ee0071699a604
- https://git.kernel.org/stable/c/b972eff874637402ddc4a7dd11fb22538a0b6d28
- https://git.kernel.org/stable/c/ca6bc277430d90375452b60b047763a090b7673e
- https://git.kernel.org/stable/c/fd24be23abf3e94260be0f00bb42c7e91d495f87
- https://git.kernel.org/stable/c/032e288097a553db5653af552dd8035cd2a0ba96
