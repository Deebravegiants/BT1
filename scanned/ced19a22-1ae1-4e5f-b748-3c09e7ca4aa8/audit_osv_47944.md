# [M] CVE-2017-15266

## Summary
Severity: Medium
Advisory: CVE-2017-15266
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-11
Source: https://osv.dev/vulnerability/CVE-2017-15266
Type: osv

## Details
In GNU Libextractor 1.4, there is a Divide-By-Zero in EXTRACTOR_wav_extract_method in wav_extractor.c via a zero sample rate.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00000.html
- http://www.securityfocus.com/bid/101271
- http://lists.gnu.org/archive/html/bug-libextractor/2017-10/msg00002.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1499599
- http://openwall.com/lists/oss-security/2017/10/11/1
