# [C] nfsd: don't replace page in rq_pages if it's a continuation of last page

## Summary
Severity: Critical
Advisory: CVE-2023-53083
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53083
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.22, >=6.2.0 <6.2.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: don't replace page in rq_pages if it's a continuation of last page

The splice read calls nfsd_splice_actor to put the pages containing file
data into the svc_rqst->rq_pages array. It's possible however to get a
splice result that only has a partial page at the end, if (e.g.) the
filesystem hands back a short read that doesn't cover the whole page.

nfsd_splice_actor will plop the partial page into its rq_pages array and
return. Then later, when nfsd_splice_actor is called again, the
remainder of the page may end up being filled out. At this point,
nfsd_splice_actor will put the page into the array _again_ corrupting
the reply. If this is done enough times, rq_next_page will overrun the
array and corrupt the trailing fields -- the rq_respages and
rq_next_page pointers themselves.

If we've already added the page to the array in the last pass, don't add
it to the array a second time when dealing with a splice continuation.
This was originally handled properly in nfsd_splice_actor, but commit
91e23b1c3982 ("NFSD: Clean up nfsd_splice_actor()") removed the check
for it.

## References
- https://git.kernel.org/stable/c/0101067f376eb7b9afd00279270f25d5111a091d
- https://git.kernel.org/stable/c/12eca509234acb6b666802edf77408bb70d7bfca
- https://git.kernel.org/stable/c/27c934dd8832dd40fd34776f916dc201e18b319b
- https://git.kernel.org/stable/c/51ddb84baff6f09ad62b5999ece3ec172e4e3568
- https://git.kernel.org/stable/c/8235cd619db6e67f1d7d26c55f1f3e4e575c947d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53083.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53083
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
