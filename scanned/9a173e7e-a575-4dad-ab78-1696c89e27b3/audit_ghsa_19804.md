# [H] GluonCV Arbitrary File Write via TarSlip

## Summary
Severity: High
Advisory: GHSA-m724-hqmc-ggpx
CVE: CVE-2024-12216
CWE: CWE-20, CWE-22, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-m724-hqmc-ggpx
Type: github-advisory

## Affected
- PyPI: `gluoncv` — affected >=0

## Details
A vulnerability in the `ImageClassificationDataset.from_csv()` API of the `dmlc/gluon-cv` repository, version 0.10.0, allows for arbitrary file write. The function downloads and extracts `tar.gz` files from URLs without proper sanitization, making it susceptible to a TarSlip vulnerability. Attackers can exploit this by crafting malicious tar files that, when extracted, can overwrite files on the victim's system via path traversal or faked symlinks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12216
- https://github.com/dmlc/gluon-cv
- https://github.com/dmlc/gluon-cv/blob/3862e2db33ab650eff7c7c5c5891e805207027b1/gluoncv/utils/filesystem.py#L223-L229
- https://huntr.com/bounties/46081fdc-2951-4deb-a2c9-2627007bdce0
