# [H] bpf: add check for invalid name in btf_name_valid_section()

## Summary
Severity: High
Advisory: CVE-2024-46764
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46764
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: add check for invalid name in btf_name_valid_section()

If the length of the name string is 1 and the value of name[0] is NULL
byte, an OOB vulnerability occurs in btf_name_valid_section() and the
return value is true, so the invalid name passes the check.

To solve this, you need to check if the first position is NULL byte and
if the first character is printable.

## References
- https://git.kernel.org/stable/c/bb6705c3f93bed2af03d43691743d4c43e3c8e6f
- https://git.kernel.org/stable/c/c8ffe2d4d37a05ce18c71b87421443c16f8475e5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46764.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46764
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
