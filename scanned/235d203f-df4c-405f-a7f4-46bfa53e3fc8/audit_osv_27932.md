# [C] ksmbd: validate payload size in ipc response

## Summary
Severity: Critical
Advisory: CVE-2024-26811
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2024-26811
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.157, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate payload size in ipc response

If installing malicious ksmbd-tools, ksmbd.mountd can return invalid ipc
response to ksmbd kernel server. ksmbd should validate payload size of
ipc response from ksmbd.mountd to avoid memory overrun or
slab-out-of-bounds. This patch validate 3 ipc response that has payload.

## References
- https://git.kernel.org/stable/c/51a6c2af9d20203ddeeaf73314ba8854b38d01bd
- https://git.kernel.org/stable/c/76af689a45aa44714b46d1a7de4ffdf851ded896
- https://git.kernel.org/stable/c/88b7f1143b15b29cccb8392b4f38e75b7bb3e300
- https://git.kernel.org/stable/c/a637fabac554270a851033f5ab402ecb90bc479c
- https://git.kernel.org/stable/c/a677ebd8ca2f2632ccdecbad7b87641274e15aac
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6XCNJZBDMGJXRIKLGKM4RRJU4XCHPX62/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LG6L4FXO4WNWUM6W7USOH2YTRVWREM3V/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RO3RO34MLQ6WT3A7O6STQUVXW43N6W3K/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26811.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26811
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
