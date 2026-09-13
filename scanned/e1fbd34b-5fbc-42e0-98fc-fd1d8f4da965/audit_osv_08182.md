# [H] CVE-2016-1281

## Summary
Severity: High
Advisory: CVE-2016-1281
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-1281
Type: osv

## Details
Untrusted search path vulnerability in the installer for TrueCrypt 7.2 and 7.1a, VeraCrypt before 1.17-BETA, and possibly other products allows local users to execute arbitrary code with administrator privileges and conduct DLL hijacking attacks via a Trojan horse DLL in the "application directory", as demonstrated with the USP10.dll, RichEd20.dll, NTMarta.dll and SRClient.dll DLLs.

## References
- http://www.openwall.com/lists/oss-security/2016/01/11/1
- http://seclists.org/fulldisclosure/2016/Jan/22
