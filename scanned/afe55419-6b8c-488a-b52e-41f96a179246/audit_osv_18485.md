# [C] CVE-2020-27886

## Summary
Severity: Critical
Advisory: CVE-2020-27886
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-29
Source: https://osv.dev/vulnerability/CVE-2020-27886
Type: osv

## Details
An issue was discovered in EyesOfNetwork eonweb 5.3-7 through 5.3-8. The eonweb web interface is prone to a SQL injection, allowing an unauthenticated attacker to exploit the username_available function of the includes/functions.php file (which is called by login.php).

## References
- https://www.eyesofnetwork.com/en
- https://github.com/EyesOfNetworkCommunity/eonweb/issues/76
- http://download.eyesofnetwork.com/EyesOfNetwork-5.3-x86_64-bin.iso
