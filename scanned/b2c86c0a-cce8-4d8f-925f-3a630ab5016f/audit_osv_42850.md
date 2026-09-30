# [H] tracing/osnoise: Call synchronize_rcu() when unregistering

## Summary
Severity: High
Advisory: CVE-2026-72012
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72012
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing/osnoise: Call synchronize_rcu() when unregistering

This ensures that any RCU readers traversing the instance list
have finished, before releasing the reference on the tracer that
the instance points to.

## References
- https://git.kernel.org/stable/c/38366140dc8ee3568c7f0191d517e117963bd580
- https://git.kernel.org/stable/c/3c693635bb7b3a9b6645831a84fed2af46cdf249
- https://git.kernel.org/stable/c/428cedade9b2cc8e48f00742df0cfd770e77a803
- https://git.kernel.org/stable/c/dd0160a0842337f12e7694d68b184050afc6d3a4
- https://git.kernel.org/stable/c/fad36954b29592ce463254179c3043697678481f
- https://git.kernel.org/stable/c/fe58f457ad8d0a2bef4e053cfecca4b5cd266b1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72012.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72012
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
