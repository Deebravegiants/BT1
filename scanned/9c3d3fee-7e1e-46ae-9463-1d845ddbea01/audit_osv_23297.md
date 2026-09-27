# [H] CVE-2022-47090

## Summary
Severity: High
Advisory: CVE-2022-47090
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-01-24
Source: https://osv.dev/vulnerability/CVE-2022-47090
Type: osv

## Details
GPAC MP4box 2.1-DEV-rev574-g9d5bb184b contains a buffer overflow in gf_vvc_read_pps_bs_internal function of media_tools/av_parsers.c, check needed for num_exp_tile_columns

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47090.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47090
- https://github.com/gpac/gpac/issues/2341
- https://github.com/gpac/gpac/commit/48760768611f6766bf9e7378bb7cc66cebd6e49d
