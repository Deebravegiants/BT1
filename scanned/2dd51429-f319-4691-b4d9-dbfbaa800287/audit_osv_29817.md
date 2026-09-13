# [H] sched: sch_cake: fix bulk flow accounting logic for host fairness

## Summary
Severity: High
Advisory: CVE-2024-46828
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46828
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched: sch_cake: fix bulk flow accounting logic for host fairness

In sch_cake, we keep track of the count of active bulk flows per host,
when running in dst/src host fairness mode, which is used as the
round-robin weight when iterating through flows. The count of active
bulk flows is updated whenever a flow changes state.

This has a peculiar interaction with the hash collision handling: when a
hash collision occurs (after the set-associative hashing), the state of
the hash bucket is simply updated to match the new packet that collided,
and if host fairness is enabled, that also means assigning new per-host
state to the flow. For this reason, the bulk flow counters of the
host(s) assigned to the flow are decremented, before new state is
assigned (and the counters, which may not belong to the same host
anymore, are incremented again).

Back when this code was introduced, the host fairness mode was always
enabled, so the decrement was unconditional. When the configuration
flags were introduced the *increment* was made conditional, but
the *decrement* was not. Which of course can lead to a spurious
decrement (and associated wrap-around to U16_MAX).

AFAICT, when host fairness is disabled, the decrement and wrap-around
happens as soon as a hash collision occurs (which is not that common in
itself, due to the set-associative hashing). However, in most cases this
is harmless, as the value is only used when host fairness mode is
enabled. So in order to trigger an array overflow, sch_cake has to first
be configured with host fairness disabled, and while running in this
mode, a hash collision has to occur to cause the overflow. Then, the
qdisc has to be reconfigured to enable host fairness, which leads to the
array out-of-bounds because the wrapped-around value is retained and
used as an array index. It seems that syzbot managed to trigger this,
which is quite impressive in its own right.

This patch fixes the issue by introducing the same conditional check on
decrement as is used on increment.

The original bug predates the upstreaming of cake, but the commit listed
in the Fixes tag touched that code, meaning that this patch won't apply
before that.

## References
- https://git.kernel.org/stable/c/4a4eeefa514db570be025ab46d779af180e2c9bb
- https://git.kernel.org/stable/c/546ea84d07e3e324644025e2aae2d12ea4c5896e
- https://git.kernel.org/stable/c/549e407569e08459d16122341d332cb508024094
- https://git.kernel.org/stable/c/7725152b54d295b7da5e34c2f419539b30d017bd
- https://git.kernel.org/stable/c/cde71a5677971f4f1b69b25e854891dbe78066a4
- https://git.kernel.org/stable/c/d4a9039a7b3d8005b90c7b1a55a306444f0e5447
- https://git.kernel.org/stable/c/d7c01c0714c04431b5e18cf17a9ea68a553d1c3c
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46828.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46828
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
