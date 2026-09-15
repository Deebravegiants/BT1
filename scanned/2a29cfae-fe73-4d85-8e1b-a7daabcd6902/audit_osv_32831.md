# [H] drivers/rapidio/rio_cm.c: prevent possible heap overwrite

## Summary
Severity: High
Advisory: CVE-2025-38090
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-30
Source: https://osv.dev/vulnerability/CVE-2025-38090
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers/rapidio/rio_cm.c: prevent possible heap overwrite

In

riocm_cdev_ioctl(RIO_CM_CHAN_SEND)
   -> cm_chan_msg_send()
      -> riocm_ch_send()

cm_chan_msg_send() checks that userspace didn't send too much data but
riocm_ch_send() failed to check that userspace sent sufficient data.  The
result is that riocm_ch_send() can write to fields in the rio_ch_chan_hdr
which were outside the bounds of the space which cm_chan_msg_send()
allocated.

Address this by teaching riocm_ch_send() to check that the entire
rio_ch_chan_hdr was copied in from userspace.

## References
- https://git.kernel.org/stable/c/1921781ec4a8824bd0c520bf9363e28a880d14ec
- https://git.kernel.org/stable/c/1cce6ac47f4a2ac1766b8a188dc8c8f6d8df2a53
- https://git.kernel.org/stable/c/50695153d7ddde3b1696dbf0085be0033bf3ddb3
- https://git.kernel.org/stable/c/58f664614f8c3d6142ab81ae551e466dc6e092e8
- https://git.kernel.org/stable/c/6d5c6711a55c35ce09b90705546050408d9d4b61
- https://git.kernel.org/stable/c/a8b5ea2e302aa5cd00fc7addd8df53c9bde7b5f6
- https://git.kernel.org/stable/c/c03ddc183249f03fc7e057e02cae6f89144d0123
- https://git.kernel.org/stable/c/ecf5ee280b702270afb02f61b299d3dfe3ec7730
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38090.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38090
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
