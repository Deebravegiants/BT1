# [H] USB: serial: kl5kusb105: fix bulk-out buffer overflow

## Summary
Severity: High
Advisory: CVE-2026-53194
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53194
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: serial: kl5kusb105: fix bulk-out buffer overflow

klsi_105_prepare_write_buffer() is called by the generic write path
with the bulk-out buffer and its size (bulk_out_size, 64 bytes). It
stores a two-byte length header at the start of the buffer and copies
the payload from the write fifo starting at buf + KLSI_HDR_LEN, but
passes the full buffer size as the number of bytes to copy:

  count = kfifo_out_locked(&port->write_fifo, buf + KLSI_HDR_LEN,
                           size, &port->lock);

When the fifo holds at least size bytes, size bytes are copied starting
two bytes into the size-byte buffer, writing KLSI_HDR_LEN bytes past its
end. Copy at most size - KLSI_HDR_LEN bytes instead, leaving room for
the header as safe_serial already does.

Writing bulk_out_size or more bytes to the tty triggers a slab
out-of-bounds write, observed with KASAN by emulating the device with
dummy_hcd and raw-gadget:

  BUG: KASAN: slab-out-of-bounds in kfifo_copy_out+0x83/0xc0
  Write of size 64 at addr ffff888112c62202 by task python3
   kfifo_copy_out
   klsi_105_prepare_write_buffer [kl5kusb105]
   usb_serial_generic_write_start [usbserial]
  Allocated by task 139:
   usb_serial_probe [usbserial]
  The buggy address is located 2 bytes inside of allocated 64-byte region

The out-of-bounds write no longer occurs with this change applied.

## References
- https://git.kernel.org/stable/c/0a57320f71941d4e0b1307453c9a1f0939afe666
- https://git.kernel.org/stable/c/14147b7963685957839c76ba8094924e22777d79
- https://git.kernel.org/stable/c/372f33ebed747d91870f57c0a2e62884a870bffa
- https://git.kernel.org/stable/c/60af1fd82983c26604102e63a3fcc822c186cceb
- https://git.kernel.org/stable/c/70d86e355c564b5510fde61361df014f5476c83e
- https://git.kernel.org/stable/c/96d47e40bf9db4a9efd5c8fb53287a508d165f14
- https://git.kernel.org/stable/c/a1288cd700f721c1a119c4f1e8efa234e59caada
- https://git.kernel.org/stable/c/bde742b076cbe26ecc89c8c68c76ae076a524d02
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53194.json
- https://access.redhat.com/security/cve/CVE-2026-53194
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53194.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53194
- https://bugzilla.redhat.com/show_bug.cgi?id=2492703
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
