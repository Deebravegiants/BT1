# [H] CVE-2004-2779

## Summary
Severity: High
Advisory: CVE-2004-2779
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-20
Source: https://osv.dev/vulnerability/CVE-2004-2779
Type: osv

## Details
id3_utf16_deserialize() in utf16.c in libid3tag through 0.15.1b misparses ID3v2 tags encoded in UTF-16 with an odd number of bytes, triggering an endless loop allocating memory until an OOM condition is reached, leading to denial-of-service (DoS).

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=304913
- https://bugzilla.gnome.org/show_bug.cgi?id=162647
- https://sources.debian.org/patches/libid3tag/0.15.1b-13/10_utf16.dpatch/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=304913
- https://sources.debian.org/patches/libid3tag/0.15.1b-13/10_utf16.dpatch/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=304913
- https://bugzilla.gnome.org/show_bug.cgi?id=162647
