# [M] CVE-2025-8746

## Summary
Severity: Medium
Advisory: CVE-2025-8746
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-09
Source: https://osv.dev/vulnerability/CVE-2025-8746
Type: osv

## Details
A vulnerability, which was classified as problematic, was found in GNU libopts up to 27.6. Affected is the function __strstr_sse2. The manipulation leads to memory corruption. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used. This issue was initially reported to the tcpreplay project, but the code maintainer explains, that this "bug appears to be in libopts which is an external library." This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://www.gnu.org/
- https://vuldb.com/?id.319242
- https://github.com/appneta/tcpreplay/issues/957
- https://github.com/appneta/tcpreplay/issues/957#issuecomment-3124774393
- https://vuldb.com/?ctiid.319242
- https://drive.google.com/file/d/1yjKOHxvL_9xExy4QUb5x43dxci1x59ts/view?usp=sharing
- https://vuldb.com/?submit.623632
