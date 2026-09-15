# [H] NFSD: Define a proc_layoutcommit for the FlexFiles layout type

## Summary
Severity: High
Advisory: CVE-2025-40087
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-40087
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.196, >=5.16.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Define a proc_layoutcommit for the FlexFiles layout type

Avoid a crash if a pNFS client should happen to send a LAYOUTCOMMIT
operation on a FlexFiles layout.

## References
- https://git.kernel.org/stable/c/34d187e020cbda112a6c6f094f0ca5e6a8672b75
- https://git.kernel.org/stable/c/4b47a8601b71ad98833b447d465592d847b4dc77
- https://git.kernel.org/stable/c/785ec512afa80d0540f2ca797c0e56de747a6083
- https://git.kernel.org/stable/c/a156af6a4dc38c2aa7c98e89520a70fb3b3e7df4
- https://git.kernel.org/stable/c/a75994dd879401c3e24ff51c2536559f1a53ea27
- https://git.kernel.org/stable/c/ba88a53d7f5df4191583abf214214efe0cda91d2
- https://git.kernel.org/stable/c/da9129ef77786839a3ccd1d7afeeab790bceaa1d
- https://git.kernel.org/stable/c/f7353208c91ab004e0179c5fb6c365b0f132f9f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40087.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
