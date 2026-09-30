# [H] fs/ntfs3: Prevent integer overflow in hdr_first_de()

## Summary
Severity: High
Advisory: CVE-2025-22080
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22080
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Prevent integer overflow in hdr_first_de()

The "de_off" and "used" variables come from the disk so they both need to
check.  The problem is that on 32bit systems if they're both greater than
UINT_MAX - 16 then the check does work as intended because of an integer
overflow.

## References
- https://git.kernel.org/stable/c/201a2bdda13b619c4927700ffe47d387a30ced50
- https://git.kernel.org/stable/c/6bb81b94f7a9cba6bde9a905cef52a65317a8b04
- https://git.kernel.org/stable/c/85615aa442830027923fc690390fa74d17b36ae1
- https://git.kernel.org/stable/c/b9982065b82b4177ba3a7a72ce18c84921f7494d
- https://git.kernel.org/stable/c/f6d44b1aa46d317e52c21fb9314cfb20dd69e7b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22080.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22080
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
