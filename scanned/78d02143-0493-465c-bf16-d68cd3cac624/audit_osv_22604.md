# [M] CVE-2022-3303

## Summary
Severity: Medium
Advisory: CVE-2022-3303
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-27
Source: https://osv.dev/vulnerability/CVE-2022-3303
Type: osv

## Details
A race condition flaw was found in the Linux kernel sound subsystem due to improper locking. It could lead to a NULL pointer dereference while handling the SNDCTL_DSP_SYNC ioctl. A privileged local user (root or member of the audio group) could use this flaw to crash the system, resulting in a denial of service condition

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8423f0b6d513b259fdab9c9bf4aaa6188d054c2d
- https://lore.kernel.org/all/CAFcO6XN7JDM4xSXGhtusQfS2mSBcx50VJKwQpCq=WeLt57aaZA%40mail.gmail.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3303.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3303
- https://www.debian.org/security/2022/dsa-5257
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
