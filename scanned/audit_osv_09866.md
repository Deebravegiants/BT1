# [H] CVE-2017-11742

## Summary
Severity: High
Advisory: CVE-2017-11742
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-30
Source: https://osv.dev/vulnerability/CVE-2017-11742
Type: osv

## Details
The writeRandomBytes_RtlGenRandom function in xmlparse.c in libexpat in Expat 2.2.1 and 2.2.2 on Windows allows local users to gain privileges via a Trojan horse ADVAPI32.DLL in the current working directory because of an untrusted search path, aka DLL hijacking.

## References
- http://www.securityfocus.com/bid/100147
- https://github.com/libexpat/libexpat/issues/82
