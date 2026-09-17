# [C] JLSEC-2026-133

## Summary
Severity: Critical
Advisory: JLSEC-2026-133
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-133
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=0 <3.2.4+0

## Details
Due to a failure in validating the number of scanline samples of a OpenEXR file containing deep scanline data, Academy Software Foundation OpenEX image parsing library version 3.2.1 and prior is susceptible to a heap-based buffer overflow vulnerability. This issue was resolved as of versions v3.2.2 and v3.1.12 of the affected library.

## References
- http://seclists.org/fulldisclosure/2024/Sep/32
- http://seclists.org/fulldisclosure/2024/Sep/34
- http://seclists.org/fulldisclosure/2024/Sep/36
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LSB6DB5LAKGPLRXEF5HDNGUMT7GIFT2C/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWMINVKQLSUHECXBSQMZFCSDRIHFOJJI/
- https://takeonme.org/cves/CVE-2023-5841.html
