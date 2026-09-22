# [H] exfat: fix double free in delayed_free

## Summary
Severity: High
Advisory: CVE-2025-38206
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38206
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.187, >=6.2.0 <6.6.156, >=6.7.0 <6.12.108, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

exfat: fix double free in delayed_free

The double free could happen in the following path.

exfat_create_upcase_table()
        exfat_create_upcase_table() : return error
        exfat_free_upcase_table() : free ->vol_utbl
        exfat_load_default_upcase_table : return error
     exfat_kill_sb()
           delayed_free()
                  exfat_free_upcase_table() <--------- double free
This patch set ->vol_util as NULL after freeing it.

## References
- https://git.kernel.org/stable/c/13d8de1b6568dcc31a95534ced16bc0c9a67bc15
- https://git.kernel.org/stable/c/1f3d9724e16d62c7d42c67d6613b8512f2887c22
- https://git.kernel.org/stable/c/29abaf93357f4a7d083cf399d4306999e20db31d
- https://git.kernel.org/stable/c/66e84439ec2af776ce749e8540f8fdd257774152
- https://git.kernel.org/stable/c/ac65f76db9b2ff3fbc9e198c0e9aaf81b111b7d0
- https://git.kernel.org/stable/c/d3cef0e7a5c1aa6217c51faa9ce8ecac35d6e1fd
- https://git.kernel.org/stable/c/ea27703eb0efbadcd45b9949526160ed90536a72
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38206.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
