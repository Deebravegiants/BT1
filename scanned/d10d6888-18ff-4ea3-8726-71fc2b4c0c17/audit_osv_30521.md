# [H] ima: fix buffer overrun in ima_eventdigest_init_common

## Summary
Severity: High
Advisory: CVE-2024-53106
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53106
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.119, >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ima: fix buffer overrun in ima_eventdigest_init_common

Function ima_eventdigest_init() calls ima_eventdigest_init_common()
with HASH_ALGO__LAST which is then used to access the array
hash_digest_size[] leading to buffer overrun. Have a conditional
statement to handle this.

## References
- https://git.kernel.org/stable/c/1ecf0df5205cfb0907eb7984b8671257965a5232
- https://git.kernel.org/stable/c/8a84765c62cc0469864e2faee43aae253ad16082
- https://git.kernel.org/stable/c/923168a0631bc42fffd55087b337b1b6c54dcff5
- https://git.kernel.org/stable/c/e01aae58e818503f2ffcd34c6f7dc6f90af1057e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53106.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53106
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
