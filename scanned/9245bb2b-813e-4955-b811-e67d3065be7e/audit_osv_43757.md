# [H] net: thunderbolt: Tear down DMA paths before stopping the rings

## Summary
Severity: High
Advisory: CVE-2026-74691
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74691
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: thunderbolt: Tear down DMA paths before stopping the rings

tbnet_tear_down() stops both rings and frees their frame buffers before
calling tb_xdomain_disable_paths().  tb_ring_stop() zeroes the ring's
descriptor base and tbnet_free_buffers() unmaps and frees the pages the
frames sit in, so by the time __tb_path_deactivate_hop() polls the hop's
'pending' bit, anything still in flight has nowhere to drain to.

The teardown sequence has been in this order since the driver was added.
The setup path has not: commit ff7cd07f3064 ("net: thunderbolt: Enable
DMA paths only after rings are enabled") moved the path enable to the end
of tbnet_connected_work() and documented why:

	/* Both logins successful so enable the rings, high-speed DMA
	 * paths and start the network device queue.
	 *
	 * Note we enable the DMA paths last to make sure we have primed
	 * the Rx ring before any incoming packets are allowed to
	 * arrive.
	 */

Teardown was never updated to match, so the rings and the paths now come
down in the same order they go up instead of in reverse.

On an ASMedia ASM4242 host router the 'pending' bit then never clears:
every teardown burns the full 500 ms timeout and
__tb_path_deactivate_hop() returns -ETIMEDOUT.  Raising the timeout to
5 s does not help, so the hop is not slow to drain, it never drains
at all.

The failure is invisible above the thunderbolt core.
__tb_path_deactivate_hops() is void and only calls tb_port_warn();
tb_path_deactivate(), tb_tunnel_deactivate() and
__tb_disconnect_xdomain_paths() are void as well, and
tb_disconnect_xdomain_paths() ends in an unconditional "return 0".  So
tb_xdomain_disable_paths() reports success and the netdev_warn() below
it never fires.  Repeated teardowns eventually take the XDomain control
channel down, after which the peer node is gone and only a power cycle
brings the controller back.

Deactivating the paths first fixes it.  Measured with kretprobes on a
stock v6.17 tree with no other patches applied, on a link that was up
and had just carried traffic:

  before: __tb_path_deactivate_hop() returns 0 for the first hop, then
          -ETIMEDOUT for the second 500335 us later
  after:  0 for both, 525 us apart

Alternating the two orderings ABBA over three load levels, four
teardowns per arm: every teardown failed before the change (21 of 21
that ran), none failed after (0 of 24).  The before arms ran short
because the link died partway through.  The same split shows up when
the interface is enslaved to a bond instead of just brought down, which
is how I ran into this in the first place.  Throughput and latency after
the change are unchanged.

Hosts whose routers drain the hop despite the stale descriptor base see
no functional difference, since the paths end up deactivated either way.

## References
- https://git.kernel.org/stable/c/0da9a6d27155ad072dd76db8cd637feead99a0e0
- https://git.kernel.org/stable/c/103a9b663ac1cacb8465aeff18f84a247154a562
- https://git.kernel.org/stable/c/4dd71cb0d23d40cb58fe4261c7bd183dca66caa0
- https://git.kernel.org/stable/c/68bf02b6b4ad3f748c6db71fd77b6c0402d252f4
- https://git.kernel.org/stable/c/7cce39109206bc5497e0953806563644b88bfc44
- https://git.kernel.org/stable/c/9a482b2b117e5fa656b6d24fc01799e8ac2d4368
- https://git.kernel.org/stable/c/b5a21615f627c48dafaa6ef82a34a5b97a4352aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74691.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74691
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
