# [M] CVE-2021-45944

## Summary
Severity: Medium
Advisory: CVE-2021-45944
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45944
Type: osv

## Details
Ghostscript GhostPDL 9.50 through 9.53.3 has a use-after-free in sampled_data_sample (called from sampled_data_continue and interp).

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=7861fcad13c497728189feafb41cd57b5b50ea25
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/ghostscript/OSV-2021-237.yaml
- https://lists.debian.org/debian-lts-announce/2022/01/msg00006.html
- https://www.debian.org/security/2022/dsa-5038
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=30715
- https://github.com/google/oss-fuzz-vulns/issues/16
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=29903
