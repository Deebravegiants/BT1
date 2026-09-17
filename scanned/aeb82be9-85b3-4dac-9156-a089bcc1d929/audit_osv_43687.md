# [C] net: ipv6: clear suppressed fib6 rule result

## Summary
Severity: Critical
Advisory: CVE-2026-74581
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-74581
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.6.151, >=6.2.0 <6.12.103, >=6.7.0 <6.18.44, >=6.13.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ipv6: clear suppressed fib6 rule result

fib6_rule_suppress() drops a suppressed route with ip6_rt_put_flags(),
but leaves res->rt6 pointing at the released rt6_info.

If no later rule supplies a replacement, fib6_rule_lookup() still sees
res.rt6 and returns that stale dst to its caller. A suppressing rule can
therefore leak a released route back to rt6_lookup(), and the next put
hits rcuref_put_slowpath() from dst_release().

Clear res->rt6 when suppressing the route so suppressed lookups fall
through to the null dst instead of reusing the released one.

## References
- https://git.kernel.org/stable/c/354db6243eca59e9d187ffbf8b7955b044ce84dc
- https://git.kernel.org/stable/c/5d29b286c9de0b309e94b9ed083aa1a2f429434f
- https://git.kernel.org/stable/c/6aea62e433fe1b586202a5fee8b5807ce635e1d7
- https://git.kernel.org/stable/c/6d98c70fe0ba8c7708bfd5b2a5174d2086775daa
- https://git.kernel.org/stable/c/90c57310e266eb94e4a80d6b15a9ca131d2e82cb
- https://git.kernel.org/stable/c/9bad152c42b37499162367fe47867411e62fffa3
- https://git.kernel.org/stable/c/a341c091ca0bfae377747b1b59a3bd8ebe18a937
- https://git.kernel.org/stable/c/dc3ab04220667f254f4348572b2a0b3febff89fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74581.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
