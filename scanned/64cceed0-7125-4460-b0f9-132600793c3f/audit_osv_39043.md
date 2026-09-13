# [H] netfilter: x_tables: guard option walkers against 1-byte tail reads

## Summary
Severity: High
Advisory: CVE-2026-43452
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43452
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: x_tables: guard option walkers against 1-byte tail reads

When the last byte of options is a non-single-byte option kind, walkers
that advance with i += op[i + 1] ? : 1 can read op[i + 1] past the end
of the option area.

Add an explicit i == optlen - 1 check before dereferencing op[i + 1]
in xt_tcpudp and xt_dccp option walkers.

## References
- https://git.kernel.org/stable/c/5b18b8b35c7cded2d17b2b2604c9b0694ff48d1c
- https://git.kernel.org/stable/c/9b94f0e42ed248eb31929da84ed9f5310d7ff540
- https://git.kernel.org/stable/c/ae1e1267650638136b84c23f2b31250f0ccb6823
- https://git.kernel.org/stable/c/bc18551c6169eac5ed813778d3e3e484002dbbe5
- https://git.kernel.org/stable/c/c2a445367a496a3c25dbc940c10c8bd1cfd4c14a
- https://git.kernel.org/stable/c/c39f84e4be1be63fc60ca7141ea7b76edcea5907
- https://git.kernel.org/stable/c/cfe770220ac2dbd3e104c6b45094037455da81d4
- https://git.kernel.org/stable/c/d04800323336eebf441d153f43234eac9b833d36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43452.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43452
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
