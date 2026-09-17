# [H] ipv4: route: Prevent rt_bind_exception() from rebinding stale fnhe

## Summary
Severity: High
Advisory: CVE-2025-68241
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68241
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.15.0 <6.1.159, >=5.16.0 <6.6.117, >=6.2.0 <6.12.59, >=6.7.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: route: Prevent rt_bind_exception() from rebinding stale fnhe

The sit driver's packet transmission path calls: sit_tunnel_xmit() ->
update_or_create_fnhe(), which lead to fnhe_remove_oldest() being called
to delete entries exceeding FNHE_RECLAIM_DEPTH+random.

The race window is between fnhe_remove_oldest() selecting fnheX for
deletion and the subsequent kfree_rcu(). During this time, the
concurrent path's __mkroute_output() -> find_exception() can fetch the
soon-to-be-deleted fnheX, and rt_bind_exception() then binds it with a
new dst using a dst_hold(). When the original fnheX is freed via RCU,
the dst reference remains permanently leaked.

CPU 0                             CPU 1
__mkroute_output()
  find_exception() [fnheX]
                                  update_or_create_fnhe()
                                    fnhe_remove_oldest() [fnheX]
  rt_bind_exception() [bind dst]
                                  RCU callback [fnheX freed, dst leak]

This issue manifests as a device reference count leak and a warning in
dmesg when unregistering the net device:

  unregister_netdevice: waiting for sitX to become free. Usage count = N

Ido Schimmel provided the simple test validation method [1].

The fix clears 'oldest->fnhe_daddr' before calling fnhe_flush_routes().
Since rt_bind_exception() checks this field, setting it to zero prevents
the stale fnhe from being reused and bound to a new dst just before it
is freed.

[1]
ip netns add ns1
ip -n ns1 link set dev lo up
ip -n ns1 address add 192.0.2.1/32 dev lo
ip -n ns1 link add name dummy1 up type dummy
ip -n ns1 route add 192.0.2.2/32 dev dummy1
ip -n ns1 link add name gretap1 up arp off type gretap \
    local 192.0.2.1 remote 192.0.2.2
ip -n ns1 route add 198.51.0.0/16 dev gretap1
taskset -c 0 ip netns exec ns1 mausezahn gretap1 \
    -A 198.51.100.1 -B 198.51.0.0/16 -t udp -p 1000 -c 0 -q &
taskset -c 2 ip netns exec ns1 mausezahn gretap1 \
    -A 198.51.100.1 -B 198.51.0.0/16 -t udp -p 1000 -c 0 -q &
sleep 10
ip netns pids ns1 | xargs kill
ip netns del ns1

## References
- https://git.kernel.org/stable/c/041ab9ca6e80d8f792bb69df28ebf1ef39c06af8
- https://git.kernel.org/stable/c/0fd16ed6dc331636fb2a874c42d2f7d3156f7ff0
- https://git.kernel.org/stable/c/298f1e0694ab4edb6092d66efed93c4554e6ced1
- https://git.kernel.org/stable/c/4b7210da22429765d19460d38c30eeca72656282
- https://git.kernel.org/stable/c/69d35c12168f9c59b159ae566f77dfad9f96d7ca
- https://git.kernel.org/stable/c/ac1499fcd40fe06479e9b933347b837ccabc2a40
- https://git.kernel.org/stable/c/b84f083f50ecc736a95091691339a1b363962f0e
- https://git.kernel.org/stable/c/b8a44407bdaf2f0c5505cc7d9fc7d8da90cf9a94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68241.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68241
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
