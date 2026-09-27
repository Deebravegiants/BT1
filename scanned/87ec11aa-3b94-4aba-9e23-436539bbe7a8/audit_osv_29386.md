# [H] usb: gadget: configfs: Prevent OOB read/write in usb_string_copy()

## Summary
Severity: High
Advisory: CVE-2024-42236
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42236
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: configfs: Prevent OOB read/write in usb_string_copy()

Userspace provided string 's' could trivially have the length zero. Left
unchecked this will firstly result in an OOB read in the form
`if (str[0 - 1] == '\n') followed closely by an OOB write in the form
`str[0 - 1] = '\0'`.

There is already a validating check to catch strings that are too long.
Let's supply an additional check for invalid strings that are too short.

## References
- https://git.kernel.org/stable/c/2d16f63d8030903e5031853e79d731ee5d474e70
- https://git.kernel.org/stable/c/6d3c721e686ea6c59e18289b400cc95c76e927e0
- https://git.kernel.org/stable/c/72b8ee0d9826e8ed00e0bdfce3e46b98419b37ce
- https://git.kernel.org/stable/c/a444c3fc264119801575ab086e03fb4952f23fd0
- https://git.kernel.org/stable/c/c95fbdde87e39e5e0ae27f28bf6711edfb985caa
- https://git.kernel.org/stable/c/d1205033e912f9332c1dbefa812e6ceb0575ce0a
- https://git.kernel.org/stable/c/e8474a10c535e6a2024c3b06e37e4a3a23beb490
- https://git.kernel.org/stable/c/eecfefad0953b2f31aaefa058f7f348ff39c4bba
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42236.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42236
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
