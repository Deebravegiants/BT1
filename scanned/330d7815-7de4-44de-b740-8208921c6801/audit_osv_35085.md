# [H] staging: rtl8723bs: fix out-of-bounds read in OnBeacon ESR IE parsing

## Summary
Severity: High
Advisory: CVE-2025-68254
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68254
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.62, >=6.13.0 <6.17.12, >=6.18.0 <6.18.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix out-of-bounds read in OnBeacon ESR IE parsing

The Extended Supported Rates (ESR) IE handling in OnBeacon accessed
*(p + 1 + ielen) and *(p + 2 + ielen) without verifying that these
offsets lie within the received frame buffer. A malformed beacon with
an ESR IE positioned at the end of the buffer could cause an
out-of-bounds read, potentially triggering a kernel panic.

Add a boundary check to ensure that the ESR IE body and the subsequent
bytes are within the limits of the frame before attempting to access
them.

This prevents OOB reads caused by malformed beacon frames.

## References
- https://git.kernel.org/stable/c/38292407c2bb5b2b3131aaace4ecc7a829b40b76
- https://git.kernel.org/stable/c/502ddcc405b69fa92e0add6c1714d654504f6fd7
- https://git.kernel.org/stable/c/bb5940193d813449540d8d3a82abc045be41f48a
- https://git.kernel.org/stable/c/bf323db1d883c209880bd92f3b12503e3531c3fc
- https://git.kernel.org/stable/c/c03cb111628924827351e19baa5b073e9b0d723d
- https://git.kernel.org/stable/c/c173ce97d3f0f0c0fefa39139d6d04ba60b5db22
- https://git.kernel.org/stable/c/d1ab7f9cee22e7b8a528da9ac953e4193b96cda5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68254.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68254
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
