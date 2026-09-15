# [H] udf: Detect system inodes linked into directory hierarchy

## Summary
Severity: High
Advisory: CVE-2023-53695
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53695
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.19.278, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Detect system inodes linked into directory hierarchy

When UDF filesystem is corrupted, hidden system inodes can be linked
into directory hierarchy which is an avenue for further serious
corruption of the filesystem and kernel confusion as noticed by syzbot
fuzzed images. Refuse to access system inodes linked into directory
hierarchy and vice versa.

## References
- https://git.kernel.org/stable/c/1dc71eeb198a8daa17d0c995998a53b0b749a158
- https://git.kernel.org/stable/c/1f328751b65c49c13a312d67a3bf27766b85baf7
- https://git.kernel.org/stable/c/37e74003d81e79457535cbbdfa1603431c03fac0
- https://git.kernel.org/stable/c/85a37983ec69cc9fcd188bc37c4de15ee326355a
- https://git.kernel.org/stable/c/9e3b5ef7d02eaa6553e79b4af9bd99227280f245
- https://git.kernel.org/stable/c/a44ec34b90440ada190924f5908b97026504fdcd
- https://git.kernel.org/stable/c/d747b31e2925a2f384e7dd1901a2e5bc5f984ed8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53695.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53695
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
