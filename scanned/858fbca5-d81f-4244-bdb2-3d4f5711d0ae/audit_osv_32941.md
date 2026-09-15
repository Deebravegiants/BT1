# [H] ACPICA: Refuse to evaluate a method if arguments are missing

## Summary
Severity: High
Advisory: CVE-2025-38386
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38386
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.187, >=5.16.0 <6.1.144, >=6.2.0 <6.6.97, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPICA: Refuse to evaluate a method if arguments are missing

As reported in [1], a platform firmware update that increased the number
of method parameters and forgot to update a least one of its callers,
caused ACPICA to crash due to use-after-free.

Since this a result of a clear AML issue that arguably cannot be fixed
up by the interpreter (it cannot produce missing data out of thin air),
address it by making ACPICA refuse to evaluate a method if the caller
attempts to pass fewer arguments than expected to it.

## References
- https://git.kernel.org/stable/c/18ff4ed6a33a7e3f2097710eacc96bea7696e803
- https://git.kernel.org/stable/c/2219e49857ffd6aea1b1ca5214d3270f84623a16
- https://git.kernel.org/stable/c/4305d936abde795c2ef6ba916de8f00a50f64d2d
- https://git.kernel.org/stable/c/6fcab2791543924d438e7fa49276d0998b0a069f
- https://git.kernel.org/stable/c/ab1e8491c19eb2ea0fda81ef28e841c7cb6399f5
- https://git.kernel.org/stable/c/b49d224d1830c46e20adce2a239c454cdab426f1
- https://git.kernel.org/stable/c/c9e4da550ae196132b990bd77ed3d8f2d9747f87
- https://git.kernel.org/stable/c/d547779e72cea9865b732cd45393c4cd02b3598e
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38386.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38386
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
