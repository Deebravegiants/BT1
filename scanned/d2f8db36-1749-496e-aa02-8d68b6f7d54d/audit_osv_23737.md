# [H] bfq: Make sure bfqg for which we are queueing requests is online

## Summary
Severity: High
Advisory: CVE-2022-49411
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49411
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bfq: Make sure bfqg for which we are queueing requests is online

Bios queued into BFQ IO scheduler can be associated with a cgroup that
was already offlined. This may then cause insertion of this bfq_group
into a service tree. But this bfq_group will get freed as soon as last
bio associated with it is completed leading to use after free issues for
service tree users. Fix the problem by making sure we always operate on
online bfq_group. If the bfq_group associated with the bio is not
online, we pick the first online parent.

## References
- https://git.kernel.org/stable/c/075a53b78b815301f8d3dd1ee2cd99554e34f0dd
- https://git.kernel.org/stable/c/51f724bffa3403a5236597e6b75df7329c1ec6e9
- https://git.kernel.org/stable/c/6ee0868b0c3ccead5907685fcdcdd0c08dfe4b0b
- https://git.kernel.org/stable/c/7781c38552e6cc54ed8e9040279561340516b881
- https://git.kernel.org/stable/c/97bd6c56bdcb41079e488e31df56809e3b2ce628
- https://git.kernel.org/stable/c/ccddf8cd411c1800863ed357064e56ceffd356bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49411.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49411
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
