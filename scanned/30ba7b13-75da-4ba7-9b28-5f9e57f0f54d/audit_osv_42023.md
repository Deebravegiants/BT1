# [H] HID: hid-goodix-spi: validate report size to prevent stack buffer overflow

## Summary
Severity: High
Advisory: CVE-2026-64367
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64367
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: hid-goodix-spi: validate report size to prevent stack buffer overflow

goodix_hid_set_raw_report() builds a protocol frame in a 128-byte stack
buffer (tmp_buf), writing an 11-12 byte header followed by the
caller-supplied report data.  The HID core caps report size at
HID_MAX_BUFFER_SIZE (16384) by default, while the driver does not set
hid_ll_driver.max_buffer_size and performs no bounds checking before
copying the payload:

    memcpy(tmp_buf + tx_len, buf, len);

A hidraw SET_REPORT ioctl with a report larger than ~116 bytes
overflows the stack buffer.

Add a size check after constructing the header, rejecting reports that
would exceed the buffer capacity.

Discovered by Atuin - Automated Vulnerability Discovery Engine.

## References
- https://git.kernel.org/stable/c/835fcc8655569737e3f057d42875a96259db74c2
- https://git.kernel.org/stable/c/ad47ad624f2fce0bc44bbadb664242461a97d774
- https://git.kernel.org/stable/c/dae1d000ddfd5c2140b036e47fff0c497ae9c64b
- https://git.kernel.org/stable/c/db0a0768d09273aadadeb76730cd658d720333a4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64367.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64367
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
