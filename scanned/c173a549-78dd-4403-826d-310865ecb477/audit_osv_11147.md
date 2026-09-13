# [M] CVE-2017-6392

## Summary
Severity: Medium
Advisory: CVE-2017-6392
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2017-6392
Type: osv

## Details
An issue was discovered in Kaltura server Lynx-12.11.0. The vulnerability exists due to insufficient filtration of user-supplied data passed to the "server-Lynx-12.11.0/admin_console/web/tools/XmlJWPlayer.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- http://www.securityfocus.com/bid/96534
- https://github.com/kaltura/server/commit/041a6d5e8336f7713985b120139c8f4b6279a337
- https://github.com/kaltura/server/issues/5303
