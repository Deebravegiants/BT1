# [H] CVE-2016-9296

## Summary
Severity: High
Advisory: CVE-2016-9296
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-12
Source: https://osv.dev/vulnerability/CVE-2016-9296
Type: osv

## Details
A null pointer dereference bug affects the 16.02 and many old versions of p7zip. A lack of null pointer check for the variable folders.PackPositions in function CInArchive::ReadAndDecodePackedStreams in CPP/7zip/Archive/7z/7zIn.cpp, as used in the 7z.so library and in 7z applications, will cause a crash and a denial of service when decoding malformed 7z files.

## References
- http://www.securityfocus.com/bid/94294
- https://sourceforge.net/p/p7zip/bugs/185/
- https://github.com/yangke/7zip-null-pointer-dereference
- https://sourceforge.net/p/p7zip/discussion/383043/thread/648d34db/
