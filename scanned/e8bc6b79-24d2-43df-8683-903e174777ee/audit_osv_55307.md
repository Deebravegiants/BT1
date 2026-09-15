# [H] CVE-2025-29070

## Summary
Severity: High
Advisory: CVE-2025-29070
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-29070
Type: osv

## Details
A heap buffer overflow vulnerability has been identified in thesmooth2() in cmsgamma.c in lcms2-2.16 which allows a remote attacker to cause a denial of service. NOTE: the Supplier disputes this because "this is not exploitable as this function is never called on normal color management, is there only as a helper for low-level programming and investigation."

## References
- https://github.com/mm2/Little-CMS/issues/475
- https://github.com/mm2/Little-CMS/issues/475#issuecomment-2696785063
