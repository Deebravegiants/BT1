# [H] gfs2: Fix unlikely race in gdlm_put_lock

## Summary
Severity: High
Advisory: CVE-2025-40242
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40242
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.56, >=6.13.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: Fix unlikely race in gdlm_put_lock

In gdlm_put_lock(), there is a small window of time in which the
DFL_UNMOUNT flag has been set but the lockspace hasn't been released,
yet.  In that window, dlm may still call gdlm_ast() and gdlm_bast().
To prevent it from dereferencing freed glock objects, only free the
glock if the lockspace has actually been released.

## References
- https://git.kernel.org/stable/c/279bde3bbb0ac0bad5c729dfa85983d75a5d7641
- https://git.kernel.org/stable/c/28c4d9bc0708956c1a736a9e49fee71b65deee81
- https://git.kernel.org/stable/c/4913592a3358f6ec366b8346b733d5e2360b08e1
- https://git.kernel.org/stable/c/5fdc1474e678eea1700aa266c0b7c2c96f81dd0d
- https://git.kernel.org/stable/c/64c61b4ac645222fa7b724cef616c1f862a72a40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40242.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40242
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
