# [H] ksmbd: fix incorrect validation for num_aces field of smb_acl

## Summary
Severity: High
Advisory: CVE-2025-21994
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-21994
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix incorrect validation for num_aces field of smb_acl

parse_dcal() validate num_aces to allocate posix_ace_state_array.

if (num_aces > ULONG_MAX / sizeof(struct smb_ace *))

It is an incorrect validation that we can create an array of size ULONG_MAX.
smb_acl has ->size field to calculate actual number of aces in request buffer
size. Use this to check invalid num_aces.

## References
- https://git.kernel.org/stable/c/1b8b67f3c5e5169535e26efedd3e422172e2db64
- https://git.kernel.org/stable/c/9c4e202abff45f8eac17989e549fc7a75095f675
- https://git.kernel.org/stable/c/a4cb17797a5d241f1e509cb5b46ed95a80c2f5fd
- https://git.kernel.org/stable/c/c3a3484d9d31b27a3db0fab91fcf191132d65236
- https://git.kernel.org/stable/c/d0f87370622a853b57e851f7d5a5452b72300f19
- https://git.kernel.org/stable/c/f6a6721802ac2f12f4c1bbe839a4c229b61866f2
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21994.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21994
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
