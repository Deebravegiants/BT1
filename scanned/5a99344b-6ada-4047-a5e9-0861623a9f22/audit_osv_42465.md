# [H] wifi: ath6kl: fix OOB access from firmware ADDBA window size

## Summary
Severity: High
Advisory: CVE-2026-68199
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68199
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath6kl: fix OOB access from firmware ADDBA window size

aggr_recv_addba_req_evt() logs a debug message when the firmware-supplied
win_sz is outside [AGGR_WIN_SZ_MIN, AGGR_WIN_SZ_MAX] but does not
return. The out-of-range win_sz is then used in TID_WINDOW_SZ() to
compute a kzalloc size and stored in rxtid->hold_q_sz, leading to
zero-size or overflowed allocations and subsequent out-of-bounds access.

Clean up any previously active aggregation session for the TID first,
then return early when win_sz is out of the valid range, instead of
proceeding with a broken allocation size.

## References
- https://git.kernel.org/stable/c/44126b6994eeb28f2103b638e698f40a1244f327
- https://git.kernel.org/stable/c/58c6c8dc2e022e1b4f3dc58725a1ca49ff470f9c
- https://git.kernel.org/stable/c/5a65fd4722416061698b0a3277222381efbc4882
- https://git.kernel.org/stable/c/67bc9af4f41f2bdba20404fbd753b2a1bd6dd352
- https://git.kernel.org/stable/c/c8e3ca7954d8233fbc54bd370c1827670f43c538
- https://git.kernel.org/stable/c/cec0a487cf38ac1f9bca240ffe8a94c5014b72f2
- https://git.kernel.org/stable/c/d4558c140782180e2c80a7588a4af9f8675adfc4
- https://git.kernel.org/stable/c/f480d9910fcfe326db3a6281df80e83af347193e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68199.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68199
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
