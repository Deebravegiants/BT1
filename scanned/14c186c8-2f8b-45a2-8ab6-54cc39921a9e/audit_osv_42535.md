# [H] can: raw: add locking for raw flags bitfield

## Summary
Severity: High
Advisory: CVE-2026-68387
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68387
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: raw: add locking for raw flags bitfield

With commit 890e5198a6e5 ("can: raw: use bitfields to store flags in
struct raw_sock") the formerly separate integer values have been integrated
into a single bitfield. This led to a read-modify-write operation when
changing a flag in raw_setsockopt() which now needs a locking to prevent
concurrent access.

Instead of adding a lock/unlock hell in each of the flag manipulations this
patch introduces a wrapper for a new raw_setsockopt_locked() function
analogue to the isotp_setsockopt[_locked]() approach in net/can/isotp.c

[mkl: use Closes tag instead of Link]

## References
- https://git.kernel.org/stable/c/00ba4bf8798242253fefc1fa6a78db1d445fd024
- https://git.kernel.org/stable/c/1e5185c090589f4146d728ab36417d8a5419f127
- https://git.kernel.org/stable/c/57791aab1129c9405f84bb0882de58967d8b44cd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68387.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68387
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
