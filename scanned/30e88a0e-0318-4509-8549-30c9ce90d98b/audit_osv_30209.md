# [H] mptcp: handle consistently DSS corruption

## Summary
Severity: High
Advisory: CVE-2024-50185
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50185
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: handle consistently DSS corruption

Bugged peer implementation can send corrupted DSS options, consistently
hitting a few warning in the data path. Use DEBUG_NET assertions, to
avoid the splat on some builds and handle consistently the error, dumping
related MIBs and performing fallback and/or reset according to the
subflow type.

## References
- https://git.kernel.org/stable/c/12c1676d598e3b8dd92a033b623b792cc2ea1ec5
- https://git.kernel.org/stable/c/35668f8ec84f6c944676e48ecc6bbc5fc8e6fe25
- https://git.kernel.org/stable/c/8bfd391bde685df7289b928ce8876a3583be4bfb
- https://git.kernel.org/stable/c/b8be15d1ae7ea4eedd547c3b3141f592fbddcd30
- https://git.kernel.org/stable/c/e32d262c89e2b22cb0640223f953b548617ed8a6
- https://git.kernel.org/stable/c/fde99e972b8f88cebe619241d7aa43d288ef666a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50185.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50185
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
