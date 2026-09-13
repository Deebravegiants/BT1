# [H] io_uring/kbuf: hold io_buffer_list reference over mmap

## Summary
Severity: High
Advisory: CVE-2024-35880
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35880
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/kbuf: hold io_buffer_list reference over mmap

If we look up the kbuf, ensure that it doesn't get unregistered until
after we're done with it. Since we're inside mmap, we cannot safely use
the io_uring lock. Rely on the fact that we can lookup the buffer list
under RCU now and grab a reference to it, preventing it from being
unregistered until we're done with it. The lookup returns the
io_buffer_list directly with it referenced.

## References
- https://git.kernel.org/stable/c/561e4f9451d65fc2f7eef564e0064373e3019793
- https://git.kernel.org/stable/c/5fd8e2359498043e0b5329a05f02d10a9eb91eb9
- https://git.kernel.org/stable/c/65938e81df2197203bda4b9a0c477e7987218d66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35880.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35880
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
