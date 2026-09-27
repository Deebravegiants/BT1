# [H] netfilter: nf_tables: use timestamp to check for set element timeout

## Summary
Severity: High
Advisory: CVE-2024-27397
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-27397
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.97, >=6.2.0 <6.6.84, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: use timestamp to check for set element timeout

Add a timestamp field at the beginning of the transaction, store it
in the nftables per-netns area.

Update set backend .insert, .deactivate and sync gc path to use the
timestamp, this avoids that an element expires while control plane
transaction is still unfinished.

.lookup and .update, which are used from packet path, still use the
current time to check if the element has expired. And .get path and dump
also since this runs lockless under rcu read size lock. Then, there is
async gc which also needs to check the current time since it runs
asynchronously from a workqueue.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0d40e8cb1d1f56a994cdd2e015af622fdca9ed4d
- https://git.kernel.org/stable/c/383182db8d58c4237772ba0764cded4938a235c3
- https://git.kernel.org/stable/c/7395dfacfff65e9938ac0889dafa1ab01e987d15
- https://git.kernel.org/stable/c/7b17de2a71e56c10335b565cc7ad238e6d984379
- https://git.kernel.org/stable/c/7fa2e2960fff8322ce2ded57b5f8e9cbc450b967
- https://git.kernel.org/stable/c/b45176b869673417ace338b87cf9cdb66e2eeb01
- https://git.kernel.org/stable/c/eaf1a29ea5d7dba8e84e9e9f3b3f47d0cd540bfe
- https://git.kernel.org/stable/c/f8dfda798650241c1692058713ca4fef8e429061
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27397.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27397
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
