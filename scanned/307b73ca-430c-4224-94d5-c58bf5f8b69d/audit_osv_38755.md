# [H] libcaca: Heap OOB write in canvas import functions caused by int overflow

## Summary
Severity: High
Advisory: CVE-2026-42046
Aliases: GHSA-4vvg-vrqv-m56w
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42046
Type: osv

## Details
libcaca is a colour ASCII art library. In 0.99.beta20 and earlier, an integer overflow vulnerability in libcaca's canvas import functionality allows an attacker to cause a controlled heap out-of-bounds write (heap overflow) by supplying a crafted file in the "caca" format. Depending on the build configuration and memory allocator, this may lead to memory corruption or remote code execution. This is the same vulnerability as CVE-2021-3410 but the fix at that time was not fully correct. Commit fb77acff9ba6bb01d53940da34fb10f20b156a23 fixes this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42046.json
- https://github.com/cacalabs/libcaca/security/advisories/GHSA-4vvg-vrqv-m56w
- https://nvd.nist.gov/vuln/detail/CVE-2026-42046
- https://github.com/cacalabs/libcaca/issues/86
- https://github.com/cacalabs/libcaca/commit/fb77acff9ba6bb01d53940da34fb10f20b156a23
