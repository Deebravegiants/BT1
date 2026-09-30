# [H] CVE-2022-39832

## Summary
Severity: High
Advisory: CVE-2022-39832
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-05
Source: https://osv.dev/vulnerability/CVE-2022-39832
Type: osv

## Details
An issue was discovered in PSPP 1.6.2. There is a heap-based buffer overflow at the function read_string in utilities/pspp-dump-sav.c, which allows attackers to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OECANCPD4WSSBJLSC3EE472M5DXRTIS4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VQKWIVW5WJ5ZQNNQFRKTRKD7J3LRLUYW/
- https://savannah.gnu.org/bugs/index.php?63000
