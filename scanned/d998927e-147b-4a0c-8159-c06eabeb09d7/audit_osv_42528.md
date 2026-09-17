# [H] tcp: fix TIME_WAIT socket reference leak on PSP policy failure

## Summary
Severity: High
Advisory: CVE-2026-68379
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68379
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: fix TIME_WAIT socket reference leak on PSP policy failure

Release the TIME_WAIT socket reference and jump to discard_it
upon PSP policy failure in both IPv4 and IPv6 receive paths.
This prevents a memory leak of tcp_tw_bucket structures.

## References
- https://git.kernel.org/stable/c/2c1931a81122c3cdc4c89448fe0442c69e21c0d5
- https://git.kernel.org/stable/c/374742a961becbbfc7fbfd1382d978a05e492741
- https://git.kernel.org/stable/c/e666af5dcc905ba694745963174d232deb478c55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68379.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68379
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
