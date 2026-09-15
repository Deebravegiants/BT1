# [H] CVE-2021-38160

## Summary
Severity: High
Advisory: CVE-2021-38160
Aliases: A-197154898, PUB-A-197154898
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-07
Source: https://osv.dev/vulnerability/CVE-2021-38160
Type: osv

## Details
In drivers/char/virtio_console.c in the Linux kernel before 5.13.4, data corruption or loss can be triggered by an untrusted device that supplies a buf->len value exceeding the buffer size. NOTE: the vendor indicates that the cited data corruption is not a vulnerability in any existing use case; the length validation was added solely for robustness in the face of anomalous host OS behavior

## References
- https://www.debian.org/security/2021/dsa-4978
- https://access.redhat.com/security/cve/cve-2021-38160
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.4
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://security.netapp.com/advisory/ntap-20210902-0010/
- https://github.com/torvalds/linux/commit/d00d8da5869a2608e97cfede094dfc5e11462a46
