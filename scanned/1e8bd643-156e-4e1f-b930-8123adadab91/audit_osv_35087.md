# [H] staging: rtl8723bs: fix out-of-bounds read in rtw_get_ie() parser

## Summary
Severity: High
Advisory: CVE-2025-68256
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68256
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.203, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.62, >=6.13.0 <6.17.12, >=6.18.0 <6.18.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix out-of-bounds read in rtw_get_ie() parser

The Information Element (IE) parser rtw_get_ie() trusted the length
byte of each IE without validating that the IE body (len bytes after
the 2-byte header) fits inside the remaining frame buffer. A malformed
frame can advertise an IE length larger than the available data, causing
the parser to increment its pointer beyond the buffer end. This results
in out-of-bounds reads or, depending on the pattern, an infinite loop.

Fix by validating that (offset + 2 + len) does not exceed the limit
before accepting the IE or advancing to the next element.

This prevents OOB reads and ensures the parser terminates safely on
malformed frames.

## References
- https://git.kernel.org/stable/c/154828bf9559b9c8421fc2f0d7f7f76b3683aaed
- https://git.kernel.org/stable/c/30c558447e90935f0de61be181bbcedf75952e00
- https://git.kernel.org/stable/c/9829c6e1b2e4180fd18315252ad6faeab6128076
- https://git.kernel.org/stable/c/a54e2b2db1b7de2e008b4f62eec35aaefcc663c5
- https://git.kernel.org/stable/c/b977eb31802817f4a37da95bf16bfdaa1eeb5fc2
- https://git.kernel.org/stable/c/c0d93d69e1472ba75b78898979b90a98ba2a2501
- https://git.kernel.org/stable/c/df191dd9f4c7249d98ada55634fa8ac19089b8cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68256.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68256
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
