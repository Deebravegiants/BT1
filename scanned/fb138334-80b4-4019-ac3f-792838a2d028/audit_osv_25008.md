# [M] CVE-2023-29469

## Summary
Severity: Medium
Advisory: CVE-2023-29469
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-29469
Type: osv

## Details
An issue was discovered in libxml2 before 2.10.4. When hashing empty dict strings in a crafted XML document, xmlDictComputeFastKey in dict.c can produce non-deterministic values, leading to various logic and memory errors, such as a double free. This behavior occurs because there is an attempt to use the first byte of an empty string, and any value is possible (not solely the '\0' value).

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.10.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29469.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29469
- https://security.netapp.com/advisory/ntap-20230601-0006/
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/510
- https://lists.debian.org/debian-lts-announce/2023/04/msg00031.html
