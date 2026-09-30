# [M] CVE-2021-45935

## Summary
Severity: Medium
Advisory: CVE-2021-45935
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45935
Type: osv

## Details
Grok 9.5.0 has a heap-based buffer overflow in openhtj2k::T1OpenHTJ2K::decompress (called from std::__1::__packaged_task_func<std::__1::__bind<grk::T1DecompressScheduler::deco and std::__1::packaged_task<int).

## References
- https://github.com/osamu620/OpenHTJ2K
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=39021
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/grok/OSV-2021-1344.yaml
