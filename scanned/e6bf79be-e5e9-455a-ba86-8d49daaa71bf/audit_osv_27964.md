# [H] bpf: Fix stackmap overflow check on 32-bit arches

## Summary
Severity: High
Advisory: CVE-2024-26883
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26883
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <6.1.83, >=5.16.0 <6.6.23, >=6.2.0 <6.7.11, >=6.7.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix stackmap overflow check on 32-bit arches

The stackmap code relies on roundup_pow_of_two() to compute the number
of hash buckets, and contains an overflow check by checking if the
resulting value is 0. However, on 32-bit arches, the roundup code itself
can overflow by doing a 32-bit left-shift of an unsigned long value,
which is undefined behaviour, so it is not guaranteed to truncate
neatly. This was triggered by syzbot on the DEVMAP_HASH type, which
contains the same check, copied from the hashtab code.

The commit in the fixes tag actually attempted to fix this, but the fix
did not account for the UB, so the fix only works on CPUs where an
overflow does result in a neat truncation to zero, which is not
guaranteed. Checking the value before rounding does not have this
problem.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0971126c8164abe2004b8536b49690a0d6005b0a
- https://git.kernel.org/stable/c/15641007df0f0d35fa28742b25c2a7db9dcd6895
- https://git.kernel.org/stable/c/21e5fa4688e1a4d3db6b72216231b24232f75c1d
- https://git.kernel.org/stable/c/43f798b9036491fb014b55dd61c4c5c3193267d0
- https://git.kernel.org/stable/c/7070b274c7866a4c5036f8d54fcaf315c64ac33a
- https://git.kernel.org/stable/c/7a4b21250bf79eef26543d35bd390448646c536b
- https://git.kernel.org/stable/c/ca1f06e72dec41ae4f76e7b1a8a97265447b46ae
- https://git.kernel.org/stable/c/d0e214acc59145ce25113f617311aa79dda39cb3
- https://git.kernel.org/stable/c/f06899582ccee09bd85d0696290e3eaca9aa042d
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26883.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26883
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
