# [C] ipv4: fib: Don't ignore error route in local/main tables.

## Summary
Severity: Critical
Advisory: CVE-2026-72421
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72421
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: fib: Don't ignore error route in local/main tables.

When CONFIG_IP_MULTIPLE_TABLES is enabled but no rule is added,
fib_lookup() performs route lookup directly on two tables.

Since the first lookup does not properly bail out, the result
of an error route in the merged local/main table could be
overwritten by another route in the default table:

  # unshare -n
  # ip link set lo up
  # ip route add 192.168.0.0/24 dev lo table 253
  # ip route add unreachable 192.168.0.0/24
  # ip route get 192.168.0.1
  192.168.0.1 dev lo table default uid 0
      cache <local>

Once a random rule is added, the error route is respected:

  # ip rule add table 0
  # ip rule del table 0
  # ip route get 192.168.0.1
  RTNETLINK answers: No route to host

Let's fix the inconsistent behaviour.

## References
- https://git.kernel.org/stable/c/49eaf1403201357762d745a35882fb734107d763
- https://git.kernel.org/stable/c/5ae18d87a45698e8244d0fcba64c658c35a7dd3d
- https://git.kernel.org/stable/c/828fad4fd418bcdb9f5d66fec0d184c52a85ec31
- https://git.kernel.org/stable/c/9127589aabdee588278e8d0d0bd3709a760a92c8
- https://git.kernel.org/stable/c/a29e95fbc51e8a1b932773fd0e259b2080881443
- https://git.kernel.org/stable/c/a668fa160247d7bbe921548cb845f607b8b9305f
- https://git.kernel.org/stable/c/b72f0db64205d9ce462038ba995d5d31eff32dc1
- https://git.kernel.org/stable/c/fd25996f57a95d56bc568c89b4921edcf334b7d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72421.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72421
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
