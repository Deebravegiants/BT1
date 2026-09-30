# [H] tmpfs: fix race on handling dquot rbtree

## Summary
Severity: High
Advisory: CVE-2024-27058
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27058
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tmpfs: fix race on handling dquot rbtree

A syzkaller reproducer found a race while attempting to remove dquot
information from the rb tree.

Fetching the rb_tree root node must also be protected by the
dqopt->dqio_sem, otherwise, giving the right timing, shmem_release_dquot()
will trigger a warning because it couldn't find a node in the tree, when
the real reason was the root node changing before the search starts:

Thread 1				Thread 2
- shmem_release_dquot()			- shmem_{acquire,release}_dquot()

- fetch ROOT				- Fetch ROOT

					- acquire dqio_sem
- wait dqio_sem

					- do something, triger a tree rebalance
					- release dqio_sem

- acquire dqio_sem
- start searching for the node, but
  from the wrong location, missing
  the node, and triggering a warning.

## References
- https://git.kernel.org/stable/c/0a69b6b3a026543bc215ccc866d0aea5579e6ce2
- https://git.kernel.org/stable/c/617d55b90e73c7b4aa2733ca6cc3f9b72d1124bb
- https://git.kernel.org/stable/c/c7077f43f30d817d10a9f8245e51576ac114b2f0
- https://git.kernel.org/stable/c/f82f184874d2761ebaa60dccf577921a0dbb3810
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27058.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27058
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
