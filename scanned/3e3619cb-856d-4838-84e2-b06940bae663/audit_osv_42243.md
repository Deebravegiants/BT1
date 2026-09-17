# [M] PyTorch torchvision GIF Decoder Out-of-bounds Heap Read

## Summary
Severity: Medium
Advisory: CVE-2026-65918
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65918
Type: osv

## Details
PyTorch torchvision through 0.28.0, fixed in commit 4e05dc2, contains an out-of-bounds heap read vulnerability in the GIF decoder's read_from_tensor callback that passes unclamped length to memcpy. Attackers can supply malicious or truncated GIF files to cause denial of service via segmentation fault or disclose adjacent heap memory contents.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65918.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65918
- https://www.vulncheck.com/advisories/pytorch-torchvision-gif-decoder-out-of-bounds-heap-read
- https://github.com/pytorch/vision/issues/9551
- https://github.com/pytorch/vision/commit/4e05dc22f5f050a9528cc0ea09ceca6cdaf8f4ed
- https://github.com/pytorch/vision/pull/9520
- https://github.com/pytorch/vision
