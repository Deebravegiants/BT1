# [M] CVE-2021-47519

## Summary
Severity: Medium
Advisory: CVE-2021-47519
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47519
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: m_can: m_can_read_fifo: fix memory leak in error branch

In m_can_read_fifo(), if the second call to m_can_fifo_read() fails,
the function jump to the out_fail label and returns without calling
m_can_receive_skb(). This means that the skb previously allocated by
alloc_can_skb() is not freed. In other terms, this is a memory leak.

This patch adds a goto label to destroy the skb if an error occurs.

Issue was found with GCC -fanalyzer, please follow the link below for
details.

## References
- https://git.kernel.org/stable/c/31cb32a590d62b18f69a9a6d433f4e69c74fdd56
- https://git.kernel.org/stable/c/75a422165477dd12d2d20aa7c9ee7c9a281c9908
