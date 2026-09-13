# [C] ntfs: detect mapping-pairs LCN accumulator overflow

## Summary
Severity: Critical
Advisory: CVE-2026-72200
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72200
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.9, >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: detect mapping-pairs LCN accumulator overflow

The NTFS mapping-pairs parser accumulates relative LCN deltas in a
signed integer.  A corrupted attribute can drive that addition past
the representable range.

One corrupt runlist shape sets the accumulated LCN to S64_MAX and
then adds a delta of 1 in the next mapping-pairs entry.

Signed overflow is undefined and can turn an invalid runlist into a
different set of physical clusters.

Check the LCN addition for overflow before storing the next run.

## References
- https://git.kernel.org/stable/c/7fb64788812d137b37f6d8724e1e41c624c1e814
- https://git.kernel.org/stable/c/7ffa8f3d30236e0ab897c30bdb01224ff1fe1c89
- https://git.kernel.org/stable/c/ec4f061f2219e0f0c6465d56d0380bf749235a53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72200.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72200
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
