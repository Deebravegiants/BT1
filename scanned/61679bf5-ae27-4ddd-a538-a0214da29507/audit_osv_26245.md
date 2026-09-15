# [H] crypto: lib/mpi - Fix unexpected pointer access in mpi_ec_init

## Summary
Severity: High
Advisory: CVE-2023-52616
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2023-52616
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.79, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: lib/mpi - Fix unexpected pointer access in mpi_ec_init

When the mpi_ec_ctx structure is initialized, some fields are not
cleared, causing a crash when referencing the field when the
structure was released. Initially, this issue was ignored because
memory for mpi_ec_ctx is allocated with the __GFP_ZERO flag.
For example, this error will be triggered when calculating the
Za value for SM2 separately.

## References
- https://git.kernel.org/stable/c/0c3687822259a7628c85cd21a3445cbe3c367165
- https://git.kernel.org/stable/c/2bb86817b33c9d704e127f92b838035a72c315b6
- https://git.kernel.org/stable/c/7abdfd45a650c714d5ebab564bb1b988f14d9b49
- https://git.kernel.org/stable/c/7ebf812b7019fd2d4d5a7ca45ef4bf3a6f4bda0a
- https://git.kernel.org/stable/c/ba3c5574203034781ac4231acf117da917efcd2a
- https://git.kernel.org/stable/c/bb44477d4506e52785693a39f03cdc6a2c5e8598
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52616.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52616
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
