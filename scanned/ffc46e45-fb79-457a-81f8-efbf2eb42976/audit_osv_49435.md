# [H] CVE-2019-12211

## Summary
Severity: High
Advisory: CVE-2019-12211
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/CVE-2019-12211
Type: osv

## Details
When FreeImage 3.18.0 reads a tiff file, it will be handed to the Load function of the PluginTIFF.cpp file, but a memcpy occurs in which the destination address and the size of the copied data are not considered, resulting in a heap overflow.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZ7KBYPPNRMX7RRWVJSX4T63E3TFB6TG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PUWVVP67FYM4GMWD7TPQ7C7JPPRUZHYE/
- https://seclists.org/bugtraq/2019/Dec/45
- https://security.gentoo.org/glsa/202107-02
- https://usn.ubuntu.com/4529-1/
- https://www.debian.org/security/2019/dsa-4593
- https://lists.debian.org/debian-lts-announce/2019/12/msg00012.html
- https://sourceforge.net/p/freeimage/discussion/36111/thread/e06734bed5/
