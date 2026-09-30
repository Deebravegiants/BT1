# [H] CVE-2021-47293

## Summary
Severity: High
Advisory: CVE-2021-47293
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47293
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_skbmod: Skip non-Ethernet packets

Currently tcf_skbmod_act() assumes that packets use Ethernet as their L2
protocol, which is not always the case.  As an example, for CAN devices:

	$ ip link add dev vcan0 type vcan
	$ ip link set up vcan0
	$ tc qdisc add dev vcan0 root handle 1: htb
	$ tc filter add dev vcan0 parent 1: protocol ip prio 10 \
		matchall action skbmod swap mac

Doing the above silently corrupts all the packets.  Do not perform skbmod
actions for non-Ethernet packets.

## References
- https://git.kernel.org/stable/c/34f1e1f657fae2891b485a3b2b95fe4d2aef9f0d
- https://git.kernel.org/stable/c/727d6a8b7ef3d25080fad228b2c4a1d4da5999c6
- https://git.kernel.org/stable/c/a88414fb1117f2fe65fb88e45ba694e1d09d5024
- https://git.kernel.org/stable/c/e4fdca366806f6bab374d1a95e626a10a3854b0c
- https://git.kernel.org/stable/c/071729150be9e1d1b851b70efb6d91ee9269d57b
