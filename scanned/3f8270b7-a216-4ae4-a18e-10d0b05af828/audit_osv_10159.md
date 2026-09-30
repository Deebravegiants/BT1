# [H] CVE-2017-14119

## Summary
Severity: High
Advisory: CVE-2017-14119
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-03
Source: https://osv.dev/vulnerability/CVE-2017-14119
Type: osv

## Details
In the EyesOfNetwork web interface (aka eonweb) 5.1-0, module\tool_all\tools\snmpwalk.php does not properly restrict popen calls, which allows remote attackers to execute arbitrary commands via shell metacharacters in a parameter.

## References
- http://kk.whitecell-club.org/index.php/archives/220/
