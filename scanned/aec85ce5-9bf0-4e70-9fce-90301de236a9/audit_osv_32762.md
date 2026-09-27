# [H] ALSA: ump: Fix buffer overflow at UMP SysEx message conversion

## Summary
Severity: High
Advisory: CVE-2025-37891
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-19
Source: https://osv.dev/vulnerability/CVE-2025-37891
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: ump: Fix buffer overflow at UMP SysEx message conversion

The conversion function from MIDI 1.0 to UMP packet contains an
internal buffer to keep the incoming MIDI bytes, and its size is 4, as
it was supposed to be the max size for a MIDI1 UMP packet data.
However, the implementation overlooked that SysEx is handled in a
different format, and it can be up to 6 bytes, as found in
do_convert_to_ump().  It leads eventually to a buffer overflow, and
may corrupt the memory when a longer SysEx message is received.

The fix is simply to extend the buffer size to 6 to fit with the SysEx
UMP message.

## References
- https://git.kernel.org/stable/c/226beac5605afbb33f8782148d188b64396145a4
- https://git.kernel.org/stable/c/42ef48dd4ebb082a1a90b5c3feeda2e68a9e32fe
- https://git.kernel.org/stable/c/56f1f30e6795b890463d9b20b11e576adf5a2f77
- https://git.kernel.org/stable/c/ce4f77bef276e7d2eb7ab03a5d08bcbaa40710ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37891.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37891
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
