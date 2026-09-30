# [H] MicroPython objslice.c slice_indices heap-based overflow

## Summary
Severity: High
Advisory: CVE-2023-7158
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-29
Source: https://osv.dev/vulnerability/CVE-2023-7158
Type: osv

## Details
A vulnerability was found in MicroPython up to 1.21.0. It has been classified as critical. Affected is the function slice_indices of the file objslice.c. The manipulation leads to heap-based buffer overflow. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 1.22.0 is able to address this issue. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-249180.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4E2HYWCZB5R4SHY4SZZZSFDMD64N4SOZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D3WWY5JY4RTJE25APB4REGDUDPATG6H7/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TEK46QAJOXXDZOWOIE2YACUOCZFWOBCK/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7158.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7158
- https://vuldb.com/?id.249180
- https://github.com/micropython/micropython/issues/13007
- https://github.com/micropython/micropython/pull/13039
- https://vuldb.com/?ctiid.249180
- https://github.com/micropython/micropython/pull/13039/commits/f397a3ec318f3ad05aa287764ae7cef32202380f
- https://github.com/micropython/micropython/releases/tag/v1.22.0
