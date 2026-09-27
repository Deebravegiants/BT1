# [M] CVE-2021-47201

## Summary
Severity: Medium
Advisory: CVE-2021-47201
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47201
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iavf: free q_vectors before queues in iavf_disable_vf

iavf_free_queues() clears adapter->num_active_queues, which
iavf_free_q_vectors() relies on, so swap the order of these two function
calls in iavf_disable_vf(). This resolves a panic encountered when the
interface is disabled and then later brought up again after PF
communication is restored.

## References
- https://git.kernel.org/stable/c/78638b47132244e3934dc5dc79f6372d5ce8e98c
- https://git.kernel.org/stable/c/89f22f129696ab53cfbc608e0a2184d0fea46ac1
- https://git.kernel.org/stable/c/926e8c83d4c1c2dac0026637eb0d492df876489e
- https://git.kernel.org/stable/c/9ef6589cac9a8c47f5544ccdf4c498093733bb3f
