# [M] CVE-2014-2875

## Summary
Severity: Medium
Advisory: CVE-2014-2875
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-02-06
Source: https://osv.dev/vulnerability/CVE-2014-2875
Type: osv

## Details
The session.lua library in CGILua 5.2 alpha 1 and 5.2 alpha 2 uses weak session IDs generated based on OS time, which allows remote attackers to hijack arbitrary sessions via a brute force attack. NOTE: CVE-2014-10399 and CVE-2014-10400 were SPLIT from this ID.

## References
- http://seclists.org/fulldisclosure/2014/Apr/318
- http://www.securityfocus.com/archive/1/531981/100/0/threaded
- http://www.syhunt.com/en/index.php?n=Advisories.Cgilua-weaksessionid
- http://seclists.org/fulldisclosure/2014/Apr/318
