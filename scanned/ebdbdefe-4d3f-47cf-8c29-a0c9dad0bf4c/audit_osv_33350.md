# [H] nvmet-fc: move lsop put work to nvmet_fc_ls_req_op

## Summary
Severity: High
Advisory: CVE-2025-40171
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40171
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.8.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-fc: move lsop put work to nvmet_fc_ls_req_op

It’s possible for more than one async command to be in flight from
__nvmet_fc_send_ls_req. For each command, a tgtport reference is taken.

In the current code, only one put work item is queued at a time, which
results in a leaked reference.

To fix this, move the work item to the nvmet_fc_ls_req_op struct, which
already tracks all resources related to the command.

## References
- https://git.kernel.org/stable/c/060ecc81240ef9d60d9485a3a5eb55a0d6e7a25c
- https://git.kernel.org/stable/c/11269c08013f4ee8b8f5edc6c56700acb34092d0
- https://git.kernel.org/stable/c/7331925c247b03b7767b8cd93cfe1b7aa2377850
- https://git.kernel.org/stable/c/7a619f8c869117ffed08365b377f66b7e1d941b4
- https://git.kernel.org/stable/c/a28112cc55013cd8cbd5d36b5115a5b851151bd9
- https://git.kernel.org/stable/c/db5a5406fb7e5337a074385c7a3e53c77f2c1bd3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40171.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40171
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
