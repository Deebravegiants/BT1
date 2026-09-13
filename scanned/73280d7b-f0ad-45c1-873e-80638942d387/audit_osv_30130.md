# [H] nouveau/dmem: Fix vulnerability in migrate_to_ram upon copy error

## Summary
Severity: High
Advisory: CVE-2024-50096
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50096
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nouveau/dmem: Fix vulnerability in migrate_to_ram upon copy error

The `nouveau_dmem_copy_one` function ensures that the copy push command is
sent to the device firmware but does not track whether it was executed
successfully.

In the case of a copy error (e.g., firmware or hardware failure), the
copy push command will be sent via the firmware channel, and
`nouveau_dmem_copy_one` will likely report success, leading to the
`migrate_to_ram` function returning a dirty HIGH_USER page to the user.

This can result in a security vulnerability, as a HIGH_USER page that may
contain sensitive or corrupted data could be returned to the user.

To prevent this vulnerability, we allocate a zero page. Thus, in case of
an error, a non-dirty (zero) page will be returned to the user.

## References
- https://git.kernel.org/stable/c/614bfb2050982d23d53d0d51c4079dba0437c883
- https://git.kernel.org/stable/c/697e3ddcf1f8b68bd531fc34eead27c000bdf3e1
- https://git.kernel.org/stable/c/73f75d2b5aee5a735cf64b8ab4543d5c20dbbdd9
- https://git.kernel.org/stable/c/835745a377a4519decd1a36d6b926e369b3033e2
- https://git.kernel.org/stable/c/8c3de9282dde21ce3c1bf1bde3166a4510547aa9
- https://git.kernel.org/stable/c/ab4d113b6718b076046018292f821d5aa4b844f8
- https://git.kernel.org/stable/c/fd9bb7e996bab9b9049fffe3f3d3b50dee191d27
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50096.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50096
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
