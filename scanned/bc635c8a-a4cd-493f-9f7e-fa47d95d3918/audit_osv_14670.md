# [H] CVE-2019-10669

## Summary
Severity: High
Advisory: CVE-2019-10669
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-10669
Type: osv

## Details
An issue was discovered in LibreNMS through 1.47. There is a command injection vulnerability in html/includes/graphs/device/collectd.inc.php where user supplied parameters are filtered with the mysqli_escape_real_string function. This function is not the appropriate function to sanitize command arguments as it does not escape a number of command line syntax characters such as ` (backtick), allowing an attacker to inject commands into the variable $rrd_cmd, which gets executed via passthru().

## References
- http://packetstormsecurity.com/files/154391/LibreNMS-Collectd-Command-Injection.html
- https://www.darkmatter.ae/xen1thlabs/librenms-command-injection-vulnerability-xl-19-017/
