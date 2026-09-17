# [M] CVE-2017-6393

## Summary
Severity: Medium
Advisory: CVE-2017-6393
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2017-6393
Type: osv

## Details
An issue was discovered in NagVis 1.9b12. The vulnerability exists due to insufficient filtration of user-supplied data passed to the "nagvis-master/share/userfiles/gadgets/std_table.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- http://www.securityfocus.com/bid/96537
- https://github.com/NagVis/nagvis/issues/91
