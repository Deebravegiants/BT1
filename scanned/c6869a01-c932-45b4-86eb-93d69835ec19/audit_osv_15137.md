# [C] CVE-2019-13917

## Summary
Severity: Critical
Advisory: CVE-2019-13917
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-13917
Type: osv

## Details
Exim 4.85 through 4.92 (fixed in 4.92.1) allows remote code execution as root in some unusual configurations that use the ${sort } expansion for items that can be controlled by an attacker (e.g., $local_part or $domain).

## References
- http://www.openwall.com/lists/oss-security/2019/07/26/5
- https://seclists.org/bugtraq/2019/Jul/51
- https://security.gentoo.org/glsa/201909-06
- https://www.debian.org/security/2019/dsa-4488
- http://exim.org/static/doc/security/CVE-2019-13917.txt
