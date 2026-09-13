# [H] CVE-2017-20006

## Summary
Severity: High
Advisory: CVE-2017-20006
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-01
Source: https://osv.dev/vulnerability/CVE-2017-20006
Type: osv

## Details
UnRAR 5.6.1.2 and 5.6.1.3 has a heap-based buffer overflow in Unpack::CopyString (called from Unpack::Unpack5 and CmdExtract::ExtractCurrentFile).

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/unrar/OSV-2017-104.yaml
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=4373
- https://github.com/aawc/unrar/commit/0ff832d31470471803b175cfff4e40c1b08ee779
