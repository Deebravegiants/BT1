# [M] BIT-gdal-2021-45943

## Summary
Severity: Medium
Advisory: BIT-gdal-2021-45943
Aliases: CVE-2021-45943, PYSEC-2022-43065
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gdal-2021-45943
Type: osv

## Affected
- Bitnami: `gdal` — affected >=3.3.0 <3.4.1

## Details
GDAL 3.3.0 through 3.4.0 has a heap-based buffer overflow in PCIDSK::CPCIDSKFile::ReadFromFile (called from PCIDSK::CPCIDSKSegment::ReadFromFile and PCIDSK::CPCIDSKBinarySegment::CPCIDSKBinarySegment).

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=41993
- https://github.com/OSGeo/gdal/commit/1ca6a3e5168c200763fa46d8aa7e698d0b757e7e
- https://github.com/OSGeo/gdal/pull/4944
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/gdal/OSV-2021-1651.yaml
- https://lists.debian.org/debian-lts-announce/2022/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00040.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JBPJGXY7IYY65NVJBLP3RONXE7ZBVCNU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P23E4DEHY5FJCR5VJ46I6TO32DT7Y3T4/
- https://security.gentoo.org/glsa/202210-15
- https://www.debian.org/security/2022/dsa-5239
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-45943
