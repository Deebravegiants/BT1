# [H] Arbitrary Code Injection in Cura

## Summary
Severity: High
Advisory: CVE-2024-8374
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-8374
Type: osv

## Details
UltiMaker Cura slicer versions 5.7.0-beta.1 through 5.7.2 are vulnerable to code injection via the 3MF format reader (/plugins/ThreeMFReader.py). The vulnerability arises from improper handling of the drop_to_buildplate property within 3MF files, which are ZIP archives containing the model data. When a 3MF file is loaded in Cura, the value of the drop_to_buildplate property is passed to the Python eval() function without proper sanitization, allowing an attacker to execute arbitrary code by crafting a malicious 3MF file. This vulnerability poses a significant risk as 3MF files are commonly shared via 3D model databases.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8374.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8374
- https://github.com/Ultimaker/Cura/commit/285a241eb28da3188c977f85d68937c0dad79c50
- https://github.com/Ultimaker/Cura
