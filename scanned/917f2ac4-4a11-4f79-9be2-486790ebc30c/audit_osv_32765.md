# [H] ksmbd: fix use-after-free in session logoff

## Summary
Severity: High
Advisory: CVE-2025-37899
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37899
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.159, >=6.2.0 <6.6.119, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in session logoff

The sess->user object can currently be in use by another thread, for
example if another connection has sent a session setup request to
bind to the session being free'd. The handler for that connection could
be in the smb2_sess_setup function which makes use of sess->user.

## References
- https://git.kernel.org/stable/c/02d16046cd11a5c037b28c12ffb818c56dd3ef43
- https://git.kernel.org/stable/c/2fc9feff45d92a92cd5f96487655d5be23fb7e2b
- https://git.kernel.org/stable/c/70ad6455139e26e85f48f95d0e21f351c1909342
- https://git.kernel.org/stable/c/931dc8a3670f71c45c0b1379ea4e92dafbda1aca
- https://git.kernel.org/stable/c/d5ec1d79509b3ee01de02c236f096bc050221b7f
- https://news.ycombinator.com/item?id=44081338
- https://sean.heelan.io/2025/05/22/how-i-used-o3-to-find-cve-2025-37899-a-remote-zeroday-vulnerability-in-the-linux-kernels-smb-implementation/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37899.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37899
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
