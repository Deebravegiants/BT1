# [M] LIEF vulnerable to denial of service through segmentation fault

## Summary
Severity: Medium
Advisory: GHSA-rm2x-hgr8-w343
CVE: CVE-2022-40923
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-rm2x-hgr8-w343
Type: github-advisory

## Affected
- PyPI: `lief` — affected >=0

## Details
A vulnerability in the LIEF::MachO::SegmentCommand::virtual_address function of LIEF v0.12.1 allows attackers to cause a denial of service (DOS) through a segmentation fault via a crafted MachO file. A [patch](https://github.com/lief-project/LIEF/commit/24935f654f6df700a9a062298258b9485f584502) is available at commit number 24935f654f6df700a9a062298258b9485f584502.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40923
- https://github.com/lief-project/LIEF/issues/784
- https://github.com/lief-project/LIEF/commit/24935f654f6df700a9a062298258b9485f584502
- https://github.com/lief-project/LIEF
- https://github.com/pypa/advisory-database/tree/main/vulns/lief/PYSEC-2022-43139.yaml
