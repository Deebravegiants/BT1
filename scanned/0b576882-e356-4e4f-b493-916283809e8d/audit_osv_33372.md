# [H] xfrm: delete x->tunnel as we delete x

## Summary
Severity: High
Advisory: CVE-2025-40215
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40215
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.62

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: delete x->tunnel as we delete x

The ipcomp fallback tunnels currently get deleted (from the various
lists and hashtables) as the last user state that needed that fallback
is destroyed (not deleted). If a reference to that user state still
exists, the fallback state will remain on the hashtables/lists,
triggering the WARN in xfrm_state_fini. Because of those remaining
references, the fix in commit f75a2804da39 ("xfrm: destroy xfrm_state
synchronously on net exit path") is not complete.

We recently fixed one such situation in TCP due to defered freeing of
skbs (commit 9b6412e6979f ("tcp: drop secpath at the same time as we
currently drop dst")). This can also happen due to IP reassembly: skbs
with a secpath remain on the reassembly queue until netns
destruction. If we can't guarantee that the queues are flushed by the
time xfrm_state_fini runs, there may still be references to a (user)
xfrm_state, preventing the timely deletion of the corresponding
fallback state.

Instead of chasing each instance of skbs holding a secpath one by one,
this patch fixes the issue directly within xfrm, by deleting the
fallback state as soon as the last user state depending on it has been
deleted. Destruction will still happen when the final reference is
dropped.

A separate lockdep class for the fallback state is required since
we're going to lock x->tunnel while x is locked.

## References
- https://git.kernel.org/stable/c/0da961fa46da1b37ef868d9b603bd202136f8f8e
- https://git.kernel.org/stable/c/1b28a7fae0128fa140a7dccd995182ff6cd1c67b
- https://git.kernel.org/stable/c/4b2c17d0f9be8b58bb30468bc81a4b61c985b04e
- https://git.kernel.org/stable/c/b441cf3f8c4b8576639d20c8eb4aa32917602ecd
- https://git.kernel.org/stable/c/d0e0d1097118461463b76562c7ebaabaa5b90b13
- https://git.kernel.org/stable/c/dc3636912d41770466543623cb76e7b88fdb42c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40215.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40215
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
