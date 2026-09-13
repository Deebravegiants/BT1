# [M] net/mlx5: HWS, Fix memory leak in hws_action_get_shared_stc_nic error flow

## Summary
Severity: Medium
Advisory: CVE-2025-39834
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39834
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: HWS, Fix memory leak in hws_action_get_shared_stc_nic error flow

When an invalid stc_type is provided, the function allocates memory for
shared_stc but jumps to unlock_and_out without freeing it, causing a
memory leak.

Fix by jumping to free_shared_stc label instead to ensure proper cleanup.

## References
- https://git.kernel.org/stable/c/051fd8576a2e4e95d5870c5c9f8679c5b16882e4
- https://git.kernel.org/stable/c/a630f83592cdad1253523a1b760cfe78fef6cd9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39834.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39834
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
