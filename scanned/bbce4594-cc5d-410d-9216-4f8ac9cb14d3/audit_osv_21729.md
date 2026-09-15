# [M] CVE-2021-45948

## Summary
Severity: Medium
Advisory: CVE-2021-45948
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45948
Type: osv

## Details
Open Asset Import Library (aka assimp) 5.1.0 and 5.1.1 has a heap-based buffer overflow in _m3d_safestr (called from m3d_load and Assimp::M3DWrapper::M3DWrapper).

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/assimp/OSV-2021-775.yaml
- https://security.gentoo.org/glsa/202210-01
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=34416
