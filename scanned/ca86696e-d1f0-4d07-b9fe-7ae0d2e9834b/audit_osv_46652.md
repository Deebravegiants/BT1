# [H] CVE-2014-5439

## Summary
Severity: High
Advisory: CVE-2014-5439
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-19
Source: https://osv.dev/vulnerability/CVE-2014-5439
Type: osv

## Details
Multiple Stack-based Buffer Overflow vulnerabilities exists in Sniffit prior to 0.3.7 via a crafted configuration file that will bypass Non-eXecutable bit NX, stack smashing protector SSP, and address space layout randomization ASLR protection mechanisms, which could let a malicious user execute arbitrary code.

## References
- http://packetstormsecurity.com/files/129292/Sniffit-Root-Shell.html
- http://packetstormsecurity.com/files/129292/Sniffit-Root-Shell.html
- http://packetstormsecurity.com/files/129292/Sniffit-Root-Shell.html
- http://seclists.org/fulldisclosure/2014/Nov/88
- http://www.securityfocus.com/bid/71318
