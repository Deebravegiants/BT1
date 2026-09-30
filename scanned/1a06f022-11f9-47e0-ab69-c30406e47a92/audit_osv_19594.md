# [M] CVE-2021-22563

## Summary
Severity: Medium
Advisory: CVE-2021-22563
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2021-11-01
Source: https://osv.dev/vulnerability/CVE-2021-22563
Type: osv

## Details
Invalid JPEG XL images using libjxl can cause an out of bounds access on a std::vector<std::vector<T>> when rendering splines. The OOB read access can either lead to a segfault, or rendering splines based on other process memory. It is recommended to upgrade past 0.6.0 or patch with https://github.com/libjxl/libjxl/pull/757

## References
- https://github.com/libjxl/libjxl/issues/735
- https://github.com/libjxl/libjxl/pull/757
