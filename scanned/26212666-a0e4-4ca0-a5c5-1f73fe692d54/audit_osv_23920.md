# [H] net: tun: unlink NAPI from device on destruction

## Summary
Severity: High
Advisory: CVE-2022-49672
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49672
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.251, >=4.20.0 <5.4.204, >=5.5.0 <5.10.129, >=5.11.0 <5.15.53, >=5.16.0 <5.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tun: unlink NAPI from device on destruction

Syzbot found a race between tun file and device destruction.
NAPIs live in struct tun_file which can get destroyed before
the netdev so we have to del them explicitly. The current
code is missing deleting the NAPI if the queue was detached
first.

## References
- https://git.kernel.org/stable/c/3b9bc84d311104906d2b4995a9a02d7b7ddab2db
- https://git.kernel.org/stable/c/8145f77d38de4f88b8a69e1463f5c09ba189d77c
- https://git.kernel.org/stable/c/82e729aee59acefe135fceffadcbc5b86dd4f1b9
- https://git.kernel.org/stable/c/8661d4b8faa2f7ee7a559969c0a7c57f077b1728
- https://git.kernel.org/stable/c/a8cf919022373c97a84fe596bbea544f909c485d
- https://git.kernel.org/stable/c/bec1be0a745ab420718217e3e0d9542a75108989
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49672.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49672
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
