# [H] uio_hv_generic: Let userspace take care of interrupt mask

## Summary
Severity: High
Advisory: CVE-2025-40048
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40048
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

uio_hv_generic: Let userspace take care of interrupt mask

Remove the logic to set interrupt mask by default in uio_hv_generic
driver as the interrupt mask value is supposed to be controlled
completely by the user space. If the mask bit gets changed
by the driver, concurrently with user mode operating on the ring,
the mask bit may be set when it is supposed to be clear, and the
user-mode driver will miss an interrupt which will cause a hang.

For eg- when the driver sets inbound ring buffer interrupt mask to 1,
the host does not interrupt the guest on the UIO VMBus channel.
However, setting the mask does not prevent the host from putting a
message in the inbound ring buffer. So let’s assume that happens,
the host puts a message into the ring buffer but does not interrupt.

Subsequently, the user space code in the guest sets the inbound ring
buffer interrupt mask to 0, saying “Hey, I’m ready for interrupts”.
User space code then calls pread() to wait for an interrupt.
Then one of two things happens:

* The host never sends another message. So the pread() waits forever.
* The host does send another message. But because there’s already a
  message in the ring buffer, it doesn’t generate an interrupt.
  This is the correct behavior, because the host should only send an
  interrupt when the inbound ring buffer transitions from empty to
  not-empty. Adding an additional message to a ring buffer that is not
  empty is not supposed to generate an interrupt on the guest.
  Since the guest is waiting in pread() and not removing messages from
  the ring buffer, the pread() waits forever.

This could be easily reproduced in hv_fcopy_uio_daemon if we delay
setting interrupt mask to 0.

Similarly if hv_uio_channel_cb() sets the interrupt_mask to 1,
there’s a race condition. Once user space empties the inbound ring
buffer, but before user space sets interrupt_mask to 0, the host could
put another message in the ring buffer but it wouldn’t interrupt.
Then the next pread() would hang.

Fix these by removing all instances where interrupt_mask is changed,
while keeping the one in set_event() unchanged to enable userspace
control the interrupt mask by writing 0/1 to /dev/uioX.

## References
- https://git.kernel.org/stable/c/01ce972e6f9974a7c76943bcb7e93746917db83a
- https://git.kernel.org/stable/c/2af39ab5e6dc46b835a52e80a22d0cad430985e3
- https://git.kernel.org/stable/c/37bd91f22794dc05436130d6983302cb90ecfe7e
- https://git.kernel.org/stable/c/540aac117eaea5723cef5e4cbf3035c4ac654d92
- https://git.kernel.org/stable/c/65d40acd911c7011745cbbd2aaac34eb5266d11e
- https://git.kernel.org/stable/c/a44f61f878f32071d6378e8dd7c2d47f9490c8f7
- https://git.kernel.org/stable/c/b15b7d2a1b09ef5428a8db260251897405a19496
- https://git.kernel.org/stable/c/e29587c07537929684faa365027f4b0d87521e1b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40048.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40048
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
