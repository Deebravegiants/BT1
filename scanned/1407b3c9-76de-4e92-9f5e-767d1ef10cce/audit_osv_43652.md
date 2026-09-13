# [H] Bluetooth: hci_conn: hold conn reference in abort_conn_sync()

## Summary
Severity: High
Advisory: CVE-2026-74531
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74531
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.151, >=6.7.0 <6.12.103, >=6.11.0 <6.18.44, >=6.13.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_conn: hold conn reference in abort_conn_sync()

There is theoretical UAF if the conn is freed while the hci_sync task is
running.

Hold refcount to avoid that.

## References
- https://git.kernel.org/stable/c/5761d003daa987ac81463f570713ce9c9dd204e5
- https://git.kernel.org/stable/c/64d1645f26aa49b5a86ba2fccd0bb6749ea725a6
- https://git.kernel.org/stable/c/963fb4b8e7d1ab07b4ae45bf15d41e667c88caca
- https://git.kernel.org/stable/c/e8f9fef362bab431d95371d3406bc720350290c3
- https://git.kernel.org/stable/c/fa812cfa81aa3d4a7b6ce8277979af57b3f79712
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74531.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74531
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
