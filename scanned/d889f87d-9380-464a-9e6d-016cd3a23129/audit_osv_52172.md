# [H] CVE-2021-47160

## Summary
Severity: High
Advisory: CVE-2021-47160
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47160
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: mt7530: fix VLAN traffic leaks

PCR_MATRIX field was set to all 1's when VLAN filtering is enabled, but
was not reset when it is disabled, which may cause traffic leaks:

	ip link add br0 type bridge vlan_filtering 1
	ip link add br1 type bridge vlan_filtering 1
	ip link set swp0 master br0
	ip link set swp1 master br1
	ip link set br0 type bridge vlan_filtering 0
	ip link set br1 type bridge vlan_filtering 0
	# traffic in br0 and br1 will start leaking to each other

As port_bridge_{add,del} have set up PCR_MATRIX properly, remove the
PCR_MATRIX write from mt7530_port_set_vlan_aware.

## References
- https://git.kernel.org/stable/c/474a2ddaa192777522a7499784f1d60691cd831a
- https://git.kernel.org/stable/c/4fe4e1f48ba119bdbc7c897c83b04ba0d08f5488
- https://git.kernel.org/stable/c/82ae35b6c14feae5f216913d5b433e143c756d4e
- https://git.kernel.org/stable/c/ae389812733b1b1e8e07fcc238e41db166b5c78d
- https://git.kernel.org/stable/c/b91117b66fe875723a4e79ec6263526fffdb44d2
