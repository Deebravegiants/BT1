# [C] [ceph] parse_longname(): strrchr() expects NUL-terminated string

## Summary
Severity: Critical
Advisory: CVE-2025-38660
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38660
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

[ceph] parse_longname(): strrchr() expects NUL-terminated string

... and parse_longname() is not guaranteed that.  That's the reason
why it uses kmemdup_nul() to build the argument for kstrtou64();
the problem is, kstrtou64() is not the only thing that need it.

Just get a NUL-terminated copy of the entire thing and be done
with that...

## References
- https://git.kernel.org/stable/c/101841c38346f4ca41dc1802c867da990ffb32eb
- https://git.kernel.org/stable/c/3145b2b11492d61c512bbc59660bb823bc757f48
- https://git.kernel.org/stable/c/493479af8af3ab907f49e99323777d498a4fbd2b
- https://git.kernel.org/stable/c/bb80f7618832d26f7e395f52f82b1dac76223e5f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38660.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38660
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
