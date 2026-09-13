# [H] cifs: Fix missing credit release on failure in cifs_issue_read()

## Summary
Severity: High
Advisory: CVE-2026-72356
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72356
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix missing credit release on failure in cifs_issue_read()

Fix missing release of credits in the failure path in cifs_issue_read()
lest retrying the subreq just overwrites the credits value.

## References
- https://git.kernel.org/stable/c/3a303f985c6bec8787c2ad4a16b39c14c5bcd765
- https://git.kernel.org/stable/c/86652704a7fd41a5a8459027e08640bbd1952826
- https://git.kernel.org/stable/c/b9ee1f0347bf56d019ca28ddff090234bb45b05c
- https://git.kernel.org/stable/c/c16b8c4cfb4fe2244cc33e469a93c1ab8684146b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72356.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72356
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
