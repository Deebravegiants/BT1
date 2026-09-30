# [M] GuardDog vulnerable to arbitrary file write when scanning a specially-crafted remote PyPI package

## Summary
Severity: Medium
Advisory: CVE-2022-23530
Aliases: GHSA-78m5-jpmf-ch7v, PYSEC-2022-42993
CVSS: 5.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L)
Published: 2022-12-16
Source: https://osv.dev/vulnerability/CVE-2022-23530
Type: osv

## Details
GuardDog is a CLI tool to identify malicious PyPI packages. Versions prior to v0.1.8 are vulnerable to arbitrary file write when scanning a specially-crafted remote PyPI package. Extracting files using shutil.unpack_archive() from a potentially malicious tarball without validating that the destination file path is within the intended destination directory can cause files outside the destination directory to be overwritten.  This issue is patched in version 0.1.8. Potential workarounds include using a safer module, like zipfile, and validating the location of the extracted files and discarding those with malicious paths.

## References
- https://github.com/DataDog/guarddog/blob/a1d064ceb09d39bb28deb6972bc0a278756ea91f/guarddog/scanners/package_scanner.py#L153..158
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23530.json
- https://github.com/DataDog/guarddog/security/advisories/GHSA-78m5-jpmf-ch7v
- https://nvd.nist.gov/vuln/detail/CVE-2022-23530
- https://github.com/DataDog/guarddog/commit/37c7d0767ba28f4df46117d478f97652594c491c
