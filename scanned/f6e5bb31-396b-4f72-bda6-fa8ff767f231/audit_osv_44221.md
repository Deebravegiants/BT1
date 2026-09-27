# [C] qede: fix out-of-bounds check for cqe->len_list[]

## Summary
Severity: Critical
Advisory: CVE-2026-80609
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80609
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.18.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

qede: fix out-of-bounds check for cqe->len_list[]

Move index check before element access.

## References
- https://git.kernel.org/stable/c/1aacefd074b5dcc99b8dbcd73e1c963ed5010110
- https://git.kernel.org/stable/c/6d203bdd227fca1787f8a80cf84b990936633c5a
- https://git.kernel.org/stable/c/6d46ab395803f162cdc50e8d346e5f1a4e766771
- https://git.kernel.org/stable/c/b17751a2ebc4aef3ce6be6f71ee8df92bf5ddfcd
- https://git.kernel.org/stable/c/bd3a6a083b408e96437dbd86ff543ba9ec3a788b
- https://git.kernel.org/stable/c/e30af53dca803893a29eb3bbe0539752ba435410
- https://git.kernel.org/stable/c/f9ba47fce5932c15891c89c60e76dfaca919cb8d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80609.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80609
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
