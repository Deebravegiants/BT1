# [H] wifi: iwlwifi: mvm: ensure offloading TID queue exists

## Summary
Severity: High
Advisory: CVE-2024-27056
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27056
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <6.1.132, >=6.2.0 <6.6.85, >=6.7.0 <6.7.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: ensure offloading TID queue exists

The resume code path assumes that the TX queue for the offloading TID
has been configured. At resume time it then tries to sync the write
pointer as it may have been updated by the firmware.

In the unusual event that no packets have been send on TID 0, the queue
will not have been allocated and this causes a crash. Fix this by
ensuring the queue exist at suspend time.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/35afffaddbe8d310dc61659da0b1a337b0d0addc
- https://git.kernel.org/stable/c/4903303f25f48b5a1e34e6324c7fae9ccd6b959a
- https://git.kernel.org/stable/c/78f65fbf421a61894c14a1b91fe2fb4437b3fe5f
- https://git.kernel.org/stable/c/ed35a509390ef4011ea2226da5dd6f62b73873b5
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27056.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27056
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
