# [H] can: hi311x: hi3110_can_ist(): fix potential use-after-free

## Summary
Severity: High
Advisory: CVE-2024-56651
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56651
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: hi311x: hi3110_can_ist(): fix potential use-after-free

The commit a22bd630cfff ("can: hi311x: do not report txerr and rxerr
during bus-off") removed the reporting of rxerr and txerr even in case
of correct operation (i. e. not bus-off).

The error count information added to the CAN frame after netif_rx() is
a potential use after free, since there is no guarantee that the skb
is in the same state. It might be freed or reused.

Fix the issue by postponing the netif_rx() call in case of txerr and
rxerr reporting.

## References
- https://git.kernel.org/stable/c/1128022009444faf49359bd406cd665b177cb643
- https://git.kernel.org/stable/c/4ad77eb8f2e07bcfa0e28887d3c7dbb732d92cc1
- https://git.kernel.org/stable/c/9ad86d377ef4a19c75a9c639964879a5b25a433b
- https://git.kernel.org/stable/c/bc30b2fe8c54694f8ae08a5b8a5d174d16d93075
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56651.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56651
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
