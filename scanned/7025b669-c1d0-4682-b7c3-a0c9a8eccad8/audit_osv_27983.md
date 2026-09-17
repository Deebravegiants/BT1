# [H] af_unix: Fix garbage collector racing against connect()

## Summary
Severity: High
Advisory: CVE-2024-26923
Aliases: A-336268889, ASB-A-336268889
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-24
Source: https://osv.dev/vulnerability/CVE-2024-26923
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <4.19.314, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.156, >=5.16.0 <6.1.87, >=6.2.0 <6.6.28, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_unix: Fix garbage collector racing against connect()

Garbage collector does not take into account the risk of embryo getting
enqueued during the garbage collection. If such embryo has a peer that
carries SCM_RIGHTS, two consecutive passes of scan_children() may see a
different set of children. Leading to an incorrectly elevated inflight
count, and then a dangling pointer within the gc_inflight_list.

sockets are AF_UNIX/SOCK_STREAM
S is an unconnected socket
L is a listening in-flight socket bound to addr, not in fdtable
V's fd will be passed via sendmsg(), gets inflight count bumped

connect(S, addr)	sendmsg(S, [V]); close(V)	__unix_gc()
----------------	-------------------------	-----------

NS = unix_create1()
skb1 = sock_wmalloc(NS)
L = unix_find_other(addr)
unix_state_lock(L)
unix_peer(S) = NS
			// V count=1 inflight=0

 			NS = unix_peer(S)
 			skb2 = sock_alloc()
			skb_queue_tail(NS, skb2[V])

			// V became in-flight
			// V count=2 inflight=1

			close(V)

			// V count=1 inflight=1
			// GC candidate condition met

						for u in gc_inflight_list:
						  if (total_refs == inflight_refs)
						    add u to gc_candidates

						// gc_candidates={L, V}

						for u in gc_candidates:
						  scan_children(u, dec_inflight)

						// embryo (skb1) was not
						// reachable from L yet, so V's
						// inflight remains unchanged
__skb_queue_tail(L, skb1)
unix_state_unlock(L)
						for u in gc_candidates:
						  if (u.inflight)
						    scan_children(u, inc_inflight_move_tail)

						// V count=1 inflight=2 (!)

If there is a GC-candidate listening socket, lock/unlock its state. This
makes GC wait until the end of any ongoing connect() to that socket. After
flipping the lock, a possibly SCM-laden embryo is already enqueued. And if
there is another embryo coming, it can not possibly carry SCM_RIGHTS. At
this point, unix_inflight() can not happen because unix_gc_lock is already
taken. Inflight graph remains unaffected.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/2e2a03787f4f0abc0072350654ab0ef3324d9db3
- https://git.kernel.org/stable/c/343c5372d5e17b306db5f8f3c895539b06e3177f
- https://git.kernel.org/stable/c/47d8ac011fe1c9251070e1bd64cb10b48193ec51
- https://git.kernel.org/stable/c/507cc232ffe53a352847893f8177d276c3b532a9
- https://git.kernel.org/stable/c/a36ae0ec2353015f0f6762e59f4c2dbc0c906423
- https://git.kernel.org/stable/c/b75722be422c276b699200de90527d01c602ea7c
- https://git.kernel.org/stable/c/dbdf7bec5c920200077d693193f989cb1513f009
- https://git.kernel.org/stable/c/e76c2678228f6aec74b305ae30c9374cc2f28a51
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26923.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26923
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
