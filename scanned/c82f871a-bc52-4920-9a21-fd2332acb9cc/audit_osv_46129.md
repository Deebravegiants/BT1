# [H] JLSEC-2026-71

## Summary
Severity: High
Advisory: JLSEC-2026-71
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-71
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=8.9.0+0 <9.9.1+0

## Details
A security regression (CVE-2006-5051) was discovered in OpenSSH's server (sshd). There is a race condition which can lead sshd to handle some signals in an unsafe manner. An unauthenticated, remote attacker may be able to trigger it by failing to authenticate within a set time period.

## References
- http://seclists.org/fulldisclosure/2024/Jul/18
- http://seclists.org/fulldisclosure/2024/Jul/19
- http://seclists.org/fulldisclosure/2024/Jul/20
- http://www.openwall.com/lists/oss-security/2024/07/01/12
- http://www.openwall.com/lists/oss-security/2024/07/01/13
- http://www.openwall.com/lists/oss-security/2024/07/02/1
- http://www.openwall.com/lists/oss-security/2024/07/03/1
- http://www.openwall.com/lists/oss-security/2024/07/03/11
- http://www.openwall.com/lists/oss-security/2024/07/03/2
- http://www.openwall.com/lists/oss-security/2024/07/03/3
- http://www.openwall.com/lists/oss-security/2024/07/03/4
- http://www.openwall.com/lists/oss-security/2024/07/03/5
- http://www.openwall.com/lists/oss-security/2024/07/04/1
- http://www.openwall.com/lists/oss-security/2024/07/04/2
- http://www.openwall.com/lists/oss-security/2024/07/08/2
- http://www.openwall.com/lists/oss-security/2024/07/08/3
- http://www.openwall.com/lists/oss-security/2024/07/09/2
- http://www.openwall.com/lists/oss-security/2024/07/09/5
- http://www.openwall.com/lists/oss-security/2024/07/10/1
- http://www.openwall.com/lists/oss-security/2024/07/10/2
