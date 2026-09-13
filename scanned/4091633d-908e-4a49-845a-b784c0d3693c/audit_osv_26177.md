# [H] Libtiff: segment fault in libtiff  in tiffreadrgbatileext() leading to denial of service

## Summary
Severity: High
Advisory: CVE-2023-52356
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-25
Source: https://osv.dev/vulnerability/CVE-2023-52356
Type: osv

## Details
A segment fault (SEGV) flaw was found in libtiff that could be triggered by passing a crafted tiff file to the TIFFReadRGBATileExt() API. This flaw allows a remote attacker to cause a heap-buffer overflow, leading to a denial of service.

## References
- http://seclists.org/fulldisclosure/2024/Jul/16
- http://seclists.org/fulldisclosure/2024/Jul/17
- http://seclists.org/fulldisclosure/2024/Jul/18
- http://seclists.org/fulldisclosure/2024/Jul/19
- http://seclists.org/fulldisclosure/2024/Jul/20
- http://seclists.org/fulldisclosure/2024/Jul/21
- http://seclists.org/fulldisclosure/2024/Jul/22
- http://seclists.org/fulldisclosure/2024/Jul/23
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00011.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00019.html
- https://support.apple.com/kb/HT214116
- https://support.apple.com/kb/HT214117
- https://support.apple.com/kb/HT214118
- https://support.apple.com/kb/HT214119
- https://support.apple.com/kb/HT214120
- https://support.apple.com/kb/HT214122
- https://support.apple.com/kb/HT214123
- https://support.apple.com/kb/HT214124
