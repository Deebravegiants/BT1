# [M] tildearrow Furnace FUR to VGM Converter stack-based overflow

## Summary
Severity: Medium
Advisory: CVE-2022-1211
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-04-03
Source: https://osv.dev/vulnerability/CVE-2022-1211
Type: osv

## Details
A vulnerability classified as critical has been found in tildearrow Furnace dev73. This affects the FUR to VGM converter in console mode which causes stack-based overflows and crashes. It is possible to initiate the attack remotely but it requires user-interaction. A POC has been disclosed to the public and may be used.

## References
- https://drive.google.com/file/d/1h111beVcWG8F99jRffO7_HKYEhm7Qgvb/view?usp=sharing
- https://vuldb.com/?id.196371
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1211.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1211
- https://github.com/tildearrow/furnace/issues/325
