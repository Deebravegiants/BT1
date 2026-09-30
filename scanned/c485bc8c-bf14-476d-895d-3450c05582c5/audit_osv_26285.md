# [C] ceph: blocklist the kclient when receiving corrupted snap trace

## Summary
Severity: Critical
Advisory: CVE-2023-52732
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52732
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <6.1.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: blocklist the kclient when receiving corrupted snap trace

When received corrupted snap trace we don't know what exactly has
happened in MDS side. And we shouldn't continue IOs and metadatas
access to MDS, which may corrupt or get incorrect contents.

This patch will just block all the further IO/MDS requests
immediately and then evict the kclient itself.

The reason why we still need to evict the kclient just after
blocking all the further IOs is that the MDS could revoke the caps
faster.

## References
- https://git.kernel.org/stable/c/66ec619e4591f8350f99c5269a7ce160cccc7a7c
- https://git.kernel.org/stable/c/a68e564adcaa69b0930809fb64d9d5f7d9c32ba9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52732.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52732
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
