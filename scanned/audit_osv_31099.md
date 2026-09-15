# [H] hrtimers: Handle CPU state correctly on hotplug

## Summary
Severity: High
Advisory: CVE-2024-57951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2024-57951
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

hrtimers: Handle CPU state correctly on hotplug

Consider a scenario where a CPU transitions from CPUHP_ONLINE to halfway
through a CPU hotunplug down to CPUHP_HRTIMERS_PREPARE, and then back to
CPUHP_ONLINE:

Since hrtimers_prepare_cpu() does not run, cpu_base.hres_active remains set
to 1 throughout. However, during a CPU unplug operation, the tick and the
clockevents are shut down at CPUHP_AP_TICK_DYING. On return to the online
state, for instance CFS incorrectly assumes that the hrtick is already
active, and the chance of the clockevent device to transition to oneshot
mode is also lost forever for the CPU, unless it goes back to a lower state
than CPUHP_HRTIMERS_PREPARE once.

This round-trip reveals another issue; cpu_base.online is not set to 1
after the transition, which appears as a WARN_ON_ONCE in enqueue_hrtimer().

Aside of that, the bulk of the per CPU state is not reset either, which
means there are dangling pointers in the worst case.

Address this by adding a corresponding startup() callback, which resets the
stale per CPU state and sets the online flag.

[ tglx: Make the new callback unconditionally available, remove the online
  	modification in the prepare() callback and clear the remaining
  	state in the starting callback instead of the prepare callback ]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/14984139f1f2768883332965db566ef26db609e7
- https://git.kernel.org/stable/c/15b453db41d36184cf0ccc21e7df624014ab6a1a
- https://git.kernel.org/stable/c/2f8dea1692eef2b7ba6a256246ed82c365fdc686
- https://git.kernel.org/stable/c/38492f6ee883c7b1d33338bf531a62cff69b4b28
- https://git.kernel.org/stable/c/3d41dbf82e10c44e53ea602398ab002baec27e75
- https://git.kernel.org/stable/c/95e4f62df23f4df1ce6ef897d44b8e23c260921a
- https://git.kernel.org/stable/c/a5cbbea145b400e40540c34816d16d36e0374fbc
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57951.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
