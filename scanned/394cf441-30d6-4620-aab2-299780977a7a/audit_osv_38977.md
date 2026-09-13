# [H] netfilter: nf_conntrack_h323: fix OOB read in decode_choice()

## Summary
Severity: High
Advisory: CVE-2026-43233
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43233
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_h323: fix OOB read in decode_choice()

In decode_choice(), the boundary check before get_len() uses the
variable `len`, which is still 0 from its initialization at the top of
the function:

    unsigned int type, ext, len = 0;
    ...
    if (ext || (son->attr & OPEN)) {
        BYTE_ALIGN(bs);
        if (nf_h323_error_boundary(bs, len, 0))  /* len is 0 here */
            return H323_ERROR_BOUND;
        len = get_len(bs);                        /* OOB read */

When the bitstream is exactly consumed (bs->cur == bs->end), the check
nf_h323_error_boundary(bs, 0, 0) evaluates to (bs->cur + 0 > bs->end),
which is false.  The subsequent get_len() call then dereferences
*bs->cur++, reading 1 byte past the end of the buffer.  If that byte
has bit 7 set, get_len() reads a second byte as well.

This can be triggered remotely by sending a crafted Q.931 SETUP message
with a User-User Information Element containing exactly 2 bytes of
PER-encoded data ({0x08, 0x00}) to port 1720 through a firewall with
the nf_conntrack_h323 helper active.  The decoder fully consumes the
PER buffer before reaching this code path, resulting in a 1-2 byte
heap-buffer-overflow read confirmed by AddressSanitizer.

Fix this by checking for 2 bytes (the maximum that get_len() may read)
instead of the uninitialized `len`.  This matches the pattern used at
every other get_len() call site in the same file, where the caller
checks for 2 bytes of available data before calling get_len().

## References
- https://git.kernel.org/stable/c/2a3aac4205e7d2f1aca2e3827de8cdd517d36c4a
- https://git.kernel.org/stable/c/35f1943d242e1b9f0b6e91c0c93bfb293a9f8224
- https://git.kernel.org/stable/c/53d32735d77ab56cc3fc7bd53a7d099418f19be1
- https://git.kernel.org/stable/c/7ef82863d42261817a6394c6c881bd6757a70f16
- https://git.kernel.org/stable/c/81f2fc5b0d0cf4696146f00f837596d10b92dead
- https://git.kernel.org/stable/c/baed0d9ba91d4f390da12d5039128ee897253d60
- https://git.kernel.org/stable/c/bcb50aa0b8f2b74a9fe5a1c7bee6f2657a288041
- https://git.kernel.org/stable/c/f0a83d0a4b7c127d32ac06d607a9214937716129
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43233.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
