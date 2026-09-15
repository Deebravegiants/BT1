# [H] apparmor: fix rlimit for posix cpu timers

## Summary
Severity: High
Advisory: CVE-2026-46328
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46328
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix rlimit for posix cpu timers

Posix cpu timers requires an additional step beyond setting the rlimit.
Refactor the code so its clear when what code is setting the
limit and conditionally update the posix cpu timers when appropriate.

## References
- https://git.kernel.org/stable/c/1f736dfe27c857b78f8461cd7c3dd9640be74b37
- https://git.kernel.org/stable/c/2232d7cd243833ad750cae656d1817fe43744a09
- https://git.kernel.org/stable/c/28aa93fcfb33b6d580c5df4ae8b6d13fb0e6fcd3
- https://git.kernel.org/stable/c/57d51d41b90eface809b72e0e009b50546492f1f
- https://git.kernel.org/stable/c/6ca56813f4a589f536adceb42882855d91fb1125
- https://git.kernel.org/stable/c/9bf1fa150775b0c6b794e4b6a2c0395e13777999
- https://git.kernel.org/stable/c/e1cc11550b2f66687a374536c9dfdddcefca0efe
- https://git.kernel.org/stable/c/e43818b16815c0c2bf933ef28316f8e704e5e0ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46328.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46328
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
