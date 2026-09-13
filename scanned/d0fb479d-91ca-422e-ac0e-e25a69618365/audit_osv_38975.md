# [H] net/rds: Clear reconnect pending bit

## Summary
Severity: High
Advisory: CVE-2026-43230
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43230
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/rds: Clear reconnect pending bit

When canceling the reconnect worker, care must be taken to reset the
reconnect-pending bit. If the reconnect worker has not yet been
scheduled before it is canceled, the reconnect-pending bit will stay
on forever.

## References
- https://git.kernel.org/stable/c/14eae5564053ac3973b9369dc674638f22f4765e
- https://git.kernel.org/stable/c/391200c274e90c34071b909ba12e3390b81b767f
- https://git.kernel.org/stable/c/3cf001aff71b1db1b4732a5381b012a114720664
- https://git.kernel.org/stable/c/597c46a42930c963f448720aaf5001dd4ed98af4
- https://git.kernel.org/stable/c/60b347333ec259ac7352f62cbbc365b04c065ff8
- https://git.kernel.org/stable/c/b89fc7c2523b2b0750d91840f4e52521270d70ed
- https://git.kernel.org/stable/c/ba2e3472022f44baddf000621fed150d7a599ea3
- https://git.kernel.org/stable/c/bcf034fa5f66b6a3e787f765a917934a2045cf7a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43230.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43230
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
