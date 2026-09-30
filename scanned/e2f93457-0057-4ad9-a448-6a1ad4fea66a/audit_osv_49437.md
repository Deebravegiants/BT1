# [M] CVE-2019-12213

## Summary
Severity: Medium
Advisory: CVE-2019-12213
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/CVE-2019-12213
Type: osv

## Details
When FreeImage 3.18.0 reads a special TIFF file, the TIFFReadDirectory function in PluginTIFF.cpp always returns 1, leading to stack exhaustion.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PUWVVP67FYM4GMWD7TPQ7C7JPPRUZHYE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZ7KBYPPNRMX7RRWVJSX4T63E3TFB6TG/
- https://security.gentoo.org/glsa/202107-02
- https://usn.ubuntu.com/4529-1/
- https://www.debian.org/security/2019/dsa-4593
- https://lists.debian.org/debian-lts-announce/2019/12/msg00012.html
- https://seclists.org/bugtraq/2019/Dec/45
- https://sourceforge.net/p/freeimage/discussion/36111/thread/e06734bed5/
