# [M] Heap-based Buffer Overflow in MicroPython

## Summary
Severity: Medium
Advisory: GHSA-74qm-4v7r-jw2f
CVE: CVE-2024-8946
CWE: CWE-122, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-74qm-4v7r-jw2f
Type: github-advisory

## Affected
- PyPI: `micropython-copy` — affected >=0
- PyPI: `micropython-io` — affected >=0
- PyPI: `micropython-os-path` — affected >=0
- PyPI: `micropython-string` — affected >=0

## Details
A vulnerability was found in MicroPython 1.23.0. It has been classified as critical. Affected is the function mp_vfs_umount of the file extmod/vfs.c of the component VFS Unmount Handler. The manipulation leads to heap-based buffer overflow. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. The name of the patch is 29943546343c92334e8518695a11fc0e2ceea68b. It is recommended to apply a patch to fix this issue. In the VFS unmount process, the comparison between the mounted path string and the unmount requested string is based solely on the length of the unmount string, which can lead to a heap buffer overflow read.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8946
- https://github.com/micropython/micropython/issues/13006
- https://github.com/micropython/micropython/issues/13006#issuecomment-1820309455
- https://github.com/micropython/micropython/commit/29943546343c92334e8518695a11fc0e2ceea68b
- https://github.com/pypa/advisory-database/tree/main/vulns/micropython-copy/PYSEC-2024-91.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/micropython-io/PYSEC-2024-93.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/micropython-os-path/PYSEC-2024-95.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/micropython-string/PYSEC-2024-96.yaml
- https://vuldb.com/?ctiid.277764
- https://vuldb.com/?id.277764
- https://vuldb.com/?submit.409312
