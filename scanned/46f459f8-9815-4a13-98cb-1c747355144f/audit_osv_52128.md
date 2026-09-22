# [M] CVE-2021-47104

## Summary
Severity: Medium
Advisory: CVE-2021-47104
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47104
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/qib: Fix memory leak in qib_user_sdma_queue_pkts()

The wrong goto label was used for the error case and missed cleanup of the
pkt allocation.

Addresses-Coverity-ID: 1493352 ("Resource leak")

## References
- https://git.kernel.org/stable/c/0aaec9c5f60754b56f84460ea439b8c5e91f4caa
- https://git.kernel.org/stable/c/1ced0a3015a95c6a6db45e37250912c4c86697ab
- https://git.kernel.org/stable/c/76b648063eb36c72dfc0a6896de8a0a7d2c7841c
- https://git.kernel.org/stable/c/79dcbd8176152b860028b62f81a635d987365752
- https://git.kernel.org/stable/c/7cf6466e00a77b0a914b7b2c28a1fc7947d55e59
- https://git.kernel.org/stable/c/aefcc25f3a0cd28a87d11d41d30419a12cd26a34
- https://git.kernel.org/stable/c/bee90911e0138c76ee67458ac0d58b38a3190f65
- https://git.kernel.org/stable/c/d53456492b5d02033c73dfa0f3b94c86337791ba
