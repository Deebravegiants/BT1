# [H] CVE-2025-60464

## Summary
Severity: High
Advisory: CVE-2025-60464
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2025-60464
Type: osv

## Details
A use-after-free in the gf_sei_load_from_state_internal function (/filters/sei_load.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted MPEG-2 TS file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/26/4
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/32/32_filters_sei_load_c_225_in_gf_sei_load_from_state_internal
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/32/README.md
- https://infosec.exchange/@sigdevel/116778370895014131
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60464.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60464
- https://github.com/gpac/gpac/issues/3278
- https://github.com/gpac/gpac/commit/8f404bd581e455267482f86272169a742f654b97
