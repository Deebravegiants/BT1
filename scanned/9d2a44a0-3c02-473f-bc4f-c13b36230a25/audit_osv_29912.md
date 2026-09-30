# [C] icmp: change the order of rate limits

## Summary
Severity: Critical
Advisory: CVE-2024-47678
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47678
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

icmp: change the order of rate limits

ICMP messages are ratelimited :

After the blamed commits, the two rate limiters are applied in this order:

1) host wide ratelimit (icmp_global_allow())

2) Per destination ratelimit (inetpeer based)

In order to avoid side-channels attacks, we need to apply
the per destination check first.

This patch makes the following change :

1) icmp_global_allow() checks if the host wide limit is reached.
   But credits are not yet consumed. This is deferred to 3)

2) The per destination limit is checked/updated.
   This might add a new node in inetpeer tree.

3) icmp_global_consume() consumes tokens if prior operations succeeded.

This means that host wide ratelimit is still effective
in keeping inetpeer tree small even under DDOS.

As a bonus, I removed icmp_global.lock as the fast path
can use a lock-free operation.

## References
- https://git.kernel.org/stable/c/483397b4ba280813e4a9c161a0a85172ddb43d19
- https://git.kernel.org/stable/c/662ec52260cc07b9ae53ecd3925183c29d34288b
- https://git.kernel.org/stable/c/8c2bd38b95f75f3d2a08c93e35303e26d480d24e
- https://git.kernel.org/stable/c/997ba8889611891f91e8ad83583466aeab6239a3
- https://git.kernel.org/stable/c/a7722921adb046e3836eb84372241f32584bdb07
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47678.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47678
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
