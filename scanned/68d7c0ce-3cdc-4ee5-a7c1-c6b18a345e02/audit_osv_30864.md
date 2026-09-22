# [H] netfilter: nf_tables: do not defer rule destruction via call_rcu

## Summary
Severity: High
Advisory: CVE-2024-56655
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56655
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: do not defer rule destruction via call_rcu

nf_tables_chain_destroy can sleep, it can't be used from call_rcu
callbacks.

Moreover, nf_tables_rule_release() is only safe for error unwinding,
while transaction mutex is held and the to-be-desroyed rule was not
exposed to either dataplane or dumps, as it deactives+frees without
the required synchronize_rcu() in-between.

nft_rule_expr_deactivate() callbacks will change ->use counters
of other chains/sets, see e.g. nft_lookup .deactivate callback, these
must be serialized via transaction mutex.

Also add a few lockdep asserts to make this more explicit.

Calling synchronize_rcu() isn't ideal, but fixing this without is hard
and way more intrusive.  As-is, we can get:

WARNING: .. net/netfilter/nf_tables_api.c:5515 nft_set_destroy+0x..
Workqueue: events nf_tables_trans_destroy_work
RIP: 0010:nft_set_destroy+0x3fe/0x5c0
Call Trace:
 <TASK>
 nf_tables_trans_destroy_work+0x6b7/0xad0
 process_one_work+0x64a/0xce0
 worker_thread+0x613/0x10d0

In case the synchronize_rcu becomes an issue, we can explore alternatives.

One way would be to allocate nft_trans_rule objects + one nft_trans_chain
object, deactivate the rules + the chain and then defer the freeing to the
nft destroy workqueue.  We'd still need to keep the synchronize_rcu path as
a fallback to handle -ENOMEM corner cases though.

## References
- https://git.kernel.org/stable/c/27f0574253f6c24c8ee4e3f0a685b75ed3a256ed
- https://git.kernel.org/stable/c/2991dc357a28b61c13ed1f7b59e9251e2b4562fb
- https://git.kernel.org/stable/c/5146c27b2780aac59876a887a5f4e793b8949862
- https://git.kernel.org/stable/c/7cf0bd232b565d9852cb25fd094f77254773e048
- https://git.kernel.org/stable/c/b04df3da1b5c6f6dc7cdccc37941740c078c4043
- https://git.kernel.org/stable/c/b0f013bebf94fe7ae75e5a53be2f2bd1cc1841e3
- https://git.kernel.org/stable/c/b8d8f53e1858178882b881b8c09f94ef0e83bf76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56655.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56655
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
