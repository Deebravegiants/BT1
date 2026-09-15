# [M] Use After Free in MicroPython

## Summary
Severity: Medium
Advisory: GHSA-pwwp-3q7j-9mx8
CVE: CVE-2024-8947
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-pwwp-3q7j-9mx8
Type: github-advisory

## Affected
- PyPI: `micropython-copy` — affected >=0
- PyPI: `micropython-io` — affected >=0

## Details
A vulnerability was found in MicroPython 1.22.2. It has been declared as critical. Affected by this vulnerability is an unknown functionality of the file py/objarray.c. The manipulation leads to use after free. The attack can be launched remotely. The complexity of an attack is rather high. The exploitation appears to be difficult. Upgrading to version 1.23.0 is able to address this issue. The identifier of the patch is 4bed614e707c0644c06e117f848fa12605c711cd. It is recommended to upgrade the affected component. In micropython objarray component, when a bytes object is resized and copied into itself, it may reference memory that has already been freed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8947
- https://github.com/micropython/micropython/issues/13283
- https://github.com/micropython/micropython/issues/13283#issuecomment-1918479709
- https://github.com/micropython/micropython/commit/4bed614e707c0644c06e117f848fa12605c711cd
- https://github.com/micropython/micropython/releases/tag/v1.23.0
- https://github.com/pypa/advisory-database/tree/main/vulns/micropython-copy/PYSEC-2024-92.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/micropython-io/PYSEC-2024-94.yaml
- https://vuldb.com/?ctiid.277765
- https://vuldb.com/?id.277765
- https://vuldb.com/?submit.409316
