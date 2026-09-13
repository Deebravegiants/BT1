# [M] CVE-2015-7506

## Summary
Severity: Medium
Advisory: CVE-2015-7506
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-02-18
Source: https://osv.dev/vulnerability/CVE-2015-7506
Type: osv

## Details
The gif_next_LZW function in libnsgif.c in Libnsgif 0.1.2 allows context-dependent attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted LZW stream in a GIF file.

## References
- http://seclists.org/fulldisclosure/2015/Dec/70
- http://seclists.org/fulldisclosure/2015/Dec/70
