# [H] netfilter: nft_flow_offload: reset dst in route object after setting up flow

## Summary
Severity: High
Advisory: CVE-2024-27403
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27403
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_flow_offload: reset dst in route object after setting up flow

dst is transferred to the flow object, route object does not own it
anymore.  Reset dst in route object, otherwise if flow_offload_add()
fails, error path releases dst twice, leading to a refcount underflow.

## References
- https://git.kernel.org/stable/c/012df10717da02367aaf92c65f9c89db206c15f4
- https://git.kernel.org/stable/c/4c167af9f6b5ae4a5dbc243d5983c295ccc2e43c
- https://git.kernel.org/stable/c/558b00a30e05753a62ecc7e05e939ca8f0241148
- https://git.kernel.org/stable/c/670548c8db44d76e40e1dfc06812bca36a61e9ae
- https://git.kernel.org/stable/c/9e0f0430389be7696396c62f037be4bf72cf93e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27403.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27403
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
