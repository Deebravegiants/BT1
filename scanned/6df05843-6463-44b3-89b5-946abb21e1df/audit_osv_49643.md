# [C] CVE-2019-15058

## Summary
Severity: Critical
Advisory: CVE-2019-15058
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-08-14
Source: https://osv.dev/vulnerability/CVE-2019-15058
Type: osv

## Details
stb_image.h (aka the stb image loader) 2.23 has a heap-based buffer over-read in stbi__tga_load, leading to Information Disclosure or Denial of Service.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=934973
- https://security-tracker.debian.org/tracker/CVE-2019-15058
- https://www.cvedetails.com/cve/CVE-2019-15058/
- https://www.mail-archive.com/debian-bugs-dist%40lists.debian.org/msg1695025.html
- https://www.suse.com/security/cve/CVE-2019-15058/
- https://github.com/nothings/stb/issues/790
