# [H] netfilter: nfnetlink_queue: do shared-unconfirmed check before segmentation

## Summary
Severity: High
Advisory: CVE-2026-45859
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45859
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nfnetlink_queue: do shared-unconfirmed check before segmentation

Ulrich reports a regression with nfqueue:

If an application did not set the 'F_GSO' capability flag and a gso
packet with an unconfirmed nf_conn entry is received all packets are
now dropped instead of queued, because the check happens after
skb_gso_segment().  In that case, we did have exclusive ownership
of the skb and its associated conntrack entry.  The elevated use
count is due to skb_clone happening via skb_gso_segment().

Move the check so that its peformed vs. the aggregated packet.

Then, annotate the individual segments except the first one so we
can do a 2nd check at reinject time.

For the normal case, where userspace does in-order reinjects, this avoids
packet drops: first reinjected segment continues traversal and confirms
entry, remaining segments observe the confirmed entry.

While at it, simplify nf_ct_drop_unconfirmed(): We only care about
unconfirmed entries with a refcnt > 1, there is no need to special-case
dying entries.

This only happens with UDP.  With TCP, the only unconfirmed packet will
be the TCP SYN, those aren't aggregated by GRO.

Next patch adds a udpgro test case to cover this scenario.

## References
- https://git.kernel.org/stable/c/207b3ebacb6113acaaec0d171d5307032c690004
- https://git.kernel.org/stable/c/23901aa6b8a2f294c4b774436b4691f3ff863a8f
- https://git.kernel.org/stable/c/79b713ef4261a8ead96af4703f89d0b5f25532e2
- https://git.kernel.org/stable/c/b740e7ddd7ca0dbfeafca3f5e52717206cf28524
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45859.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45859
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
