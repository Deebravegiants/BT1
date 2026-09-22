# [H] Bluetooth: L2CAP: do not leave dangling sk pointer on error in l2cap_sock_create()

## Summary
Severity: High
Advisory: CVE-2024-56605
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56605
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: do not leave dangling sk pointer on error in l2cap_sock_create()

bt_sock_alloc() allocates the sk object and attaches it to the provided
sock object. On error l2cap_sock_alloc() frees the sk object, but the
dangling pointer is still attached to the sock object, which may create
use-after-free in other code.

## References
- https://git.kernel.org/stable/c/61686abc2f3c2c67822aa23ce6f160467ec83d35
- https://git.kernel.org/stable/c/7c4f78cdb8e7501e9f92d291a7d956591bf73be9
- https://git.kernel.org/stable/c/8ad09ddc63ace3950ac43db6fbfe25b40f589dd6
- https://git.kernel.org/stable/c/a8677028dd5123e5e525b8195483994d87123de4
- https://git.kernel.org/stable/c/bb2f2342a6ddf7c04f9aefbbfe86104cd138e629
- https://git.kernel.org/stable/c/daa13175a6dea312a76099066cb4cbd4fc959a84
- https://git.kernel.org/stable/c/f6ad641646b67f29c7578dcd6c25813c7dcbf51e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56605.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56605
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
