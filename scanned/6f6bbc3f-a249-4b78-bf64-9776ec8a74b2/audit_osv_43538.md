# [H] wifi: wcn36xx: fix heap overflow from oversized firmware HAL response

## Summary
Severity: High
Advisory: CVE-2026-74341
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74341
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wcn36xx: fix heap overflow from oversized firmware HAL response

The firmware response dispatcher copies all synchronous HAL responses
into the 4096-byte hal_buf without validating the response length. A
response exceeding WCN36XX_HAL_BUF_SIZE causes a heap buffer overflow
with firmware-controlled content.

Add a bounds check on the response length.

## References
- https://git.kernel.org/stable/c/15545ee71301e82d26d9a31b407ed0019eb62a60
- https://git.kernel.org/stable/c/18813b90032bfaafb225906a4d2b51be4dfc02c3
- https://git.kernel.org/stable/c/1b5d8a248c3afa640bcc99fa95abcd1e36f3ee18
- https://git.kernel.org/stable/c/88a240d86d3d64521f9194abe185ac71cc74d0bd
- https://git.kernel.org/stable/c/cfc67aee0c83e7f5d43a1dad3e25c789e9cc1d92
- https://git.kernel.org/stable/c/dae9cadf0925f1cbfb71306d60490890df3870a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74341.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74341
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
