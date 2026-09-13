# [M] CVE-2021-45949

## Summary
Severity: Medium
Advisory: CVE-2021-45949
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45949
Type: osv

## Details
Ghostscript GhostPDL 9.50 through 9.54.0 has a heap-based buffer overflow in sampled_data_finish (called from sampled_data_continue and interp).

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=2a3129365d3bc0d4a41f107ef175920d1505d1f7
- https://lists.debian.org/debian-lts-announce/2022/01/msg00006.html
- https://www.debian.org/security/2022/dsa-5038
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/ghostscript/OSV-2021-803.yaml
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=34675
