# [H] Bluetooth: eir: Fix using strlen with hdev->{dev_name,short_name}

## Summary
Severity: High
Advisory: CVE-2022-50233
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-09
Source: https://osv.dev/vulnerability/CVE-2022-50233
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: eir: Fix using strlen with hdev->{dev_name,short_name}

Both dev_name and short_name are not guaranteed to be NULL terminated so
this instead use strnlen and then attempt to determine if the resulting
string needs to be truncated or not.

## References
- https://git.kernel.org/stable/c/dd7b8cdde098cf9f7c8de409b5b7bbb98f97be80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50233.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
