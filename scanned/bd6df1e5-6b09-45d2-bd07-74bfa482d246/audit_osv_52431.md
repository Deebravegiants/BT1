# [M] CVE-2021-47442

## Summary
Severity: Medium
Advisory: CVE-2021-47442
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47442
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFC: digital: fix possible memory leak in digital_in_send_sdd_req()

'skb' is allocated in digital_in_send_sdd_req(), but not free when
digital_in_send_cmd() failed, which will cause memory leak. Fix it
by freeing 'skb' if digital_in_send_cmd() return failed.

## References
- https://git.kernel.org/stable/c/50cb95487c265187289810addec5093d4fed8329
- https://git.kernel.org/stable/c/6432d7f1d1c3aa74cfe8f5e3afdf81b786c32e86
- https://git.kernel.org/stable/c/74569c78aa84f8c958f1334b465bc530906ec99a
- https://git.kernel.org/stable/c/88c890b0b9a1fb9fcd01c61ada515e8b636c34f9
- https://git.kernel.org/stable/c/fcce6e5255474ca33c27dda0cdf9bf5087278873
- https://git.kernel.org/stable/c/071bdef36391958c89af5fa2172f691b31baa212
- https://git.kernel.org/stable/c/291c932fc3692e4d211a445ba8aa35663831bac7
- https://git.kernel.org/stable/c/2bde4aca56db9fe25405d39ddb062531493a65db
