# [H] ksmbd: add refcnt to ksmbd_conn struct

## Summary
Severity: High
Advisory: CVE-2024-49988
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49988
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: add refcnt to ksmbd_conn struct

When sending an oplock break request, opinfo->conn is used,
But freed ->conn can be used on multichannel.
This patch add a reference count to the ksmbd_conn struct
so that it can be freed when it is no longer used.

## References
- https://git.kernel.org/stable/c/18f06bacc197d4ac9b518ad1c69999bc3d83e7aa
- https://git.kernel.org/stable/c/9fd3cde4628bcd3549ab95061f2bab74d2ed4f3b
- https://git.kernel.org/stable/c/e9dac92f4482a382e8c0fe1bc243da5fc3526b0c
- https://git.kernel.org/stable/c/ee426bfb9d09b29987369b897fe9b6485ac2be27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49988.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
