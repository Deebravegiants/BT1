# [H] pipe: wakeup wr_wait after setting max_usage

## Summary
Severity: High
Advisory: CVE-2023-52672
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52672
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

pipe: wakeup wr_wait after setting max_usage

Commit c73be61cede5 ("pipe: Add general notification queue support") a
regression was introduced that would lock up resized pipes under certain
conditions. See the reproducer in [1].

The commit resizing the pipe ring size was moved to a different
function, doing that moved the wakeup for pipe->wr_wait before actually
raising pipe->max_usage. If a pipe was full before the resize occured it
would result in the wakeup never actually triggering pipe_write.

Set @max_usage and @nr_accounted before waking writers if this isn't a
watch queue.

[Christian Brauner <brauner@kernel.org>: rewrite to account for watch queues]

## References
- https://git.kernel.org/stable/c/162ae0e78bdabf84ef10c1293c4ed7865cb7d3c8
- https://git.kernel.org/stable/c/3efbd114b91525bb095b8ae046382197d92126b9
- https://git.kernel.org/stable/c/68e51bdb1194f11d3452525b99c98aff6f837b24
- https://git.kernel.org/stable/c/6fb70694f8d1ac34e45246b0ac988f025e1e5b55
- https://git.kernel.org/stable/c/b87a1229d8668fbc78ebd9ca0fc797a76001c60f
- https://git.kernel.org/stable/c/e95aada4cb93d42e25c30a0ef9eb2923d9711d4a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52672.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52672
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
