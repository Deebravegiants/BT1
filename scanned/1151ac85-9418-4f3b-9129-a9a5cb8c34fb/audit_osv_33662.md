# [M] CVE-2025-48172

## Summary
Severity: Medium
Advisory: CVE-2025-48172
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-48172
Type: osv

## Details
CHMLib through 2bef8d0, as used in SumatraPDF and other products, has a chm_lib.c _chm_decompress_block integer overflow. There is a resultant heap-based buffer overflow in _chm_fetch_bytes.

## References
- https://drive.google.com/file/d/1XpulFyCGlq7Szzg5RsH-eRwZ6OyuSozl/view?usp=sharing
- https://drive.google.com/file/d/1wq51px42eoJz2VQ1Qu9ObPVQVom9T9H_/view?usp=sharing
- https://github.com/jedwing/CHMLib/blob/2bef8d063ec7d88a8de6fd9f0513ea42ac0fa21f/src/chm_lib.c#L1386
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48172.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48172
- https://github.com/sumatrapdfreader/sumatrapdf/commit/08179946a745cf1605e4b9670942ec1a6e1f4c5d
