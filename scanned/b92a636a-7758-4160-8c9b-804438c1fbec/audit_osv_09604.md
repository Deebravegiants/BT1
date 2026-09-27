# [H] CVE-2017-1000368

## Summary
Severity: High
Advisory: CVE-2017-1000368
CVSS: 8.2 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-1000368
Type: osv

## Details
Todd Miller's sudo version 1.8.20p1 and earlier is vulnerable to an input validation (embedded newlines) in the get_process_ttyname() function resulting in information disclosure and command execution.

## References
- https://usn.ubuntu.com/3968-1/
- https://usn.ubuntu.com/3968-2/
- http://www.securityfocus.com/bid/98838
- https://access.redhat.com/errata/RHSA-2017:1574
- https://kc.mcafee.com/corporate/index?page=content&id=SB10205
- https://security.gentoo.org/glsa/201710-04
- https://www.sudo.ws/alerts/linux_tty.html
