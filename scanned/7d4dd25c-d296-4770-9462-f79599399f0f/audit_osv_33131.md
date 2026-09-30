# [H] wifi: ath12k: Decrement TID on RX peer frag setup error handling

## Summary
Severity: High
Advisory: CVE-2025-39761
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39761
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: Decrement TID on RX peer frag setup error handling

Currently, TID is not decremented before peer cleanup, during error
handling path of ath12k_dp_rx_peer_frag_setup(). This could lead to
out-of-bounds access in peer->rx_tid[].

Hence, add a decrement operation for TID, before peer cleanup to
ensures proper cleanup and prevents out-of-bounds access issues when
the RX peer frag setup fails.

Found during code review. Compile tested only.

## References
- https://git.kernel.org/stable/c/7c0884fcd2ddde0544d2e77f297ae461e1f53f58
- https://git.kernel.org/stable/c/7c3e99fd4a66a5ac9c7dd32db07359666efe0002
- https://git.kernel.org/stable/c/9530d666f4376c294cdf4348c29fe3542fec980a
- https://git.kernel.org/stable/c/a3b73c72c42348bf1555fd2b00f32f941324b242
- https://git.kernel.org/stable/c/eb1e1526b82b8cf31f1ef9ca86a2647fb6cd89c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39761.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39761
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
