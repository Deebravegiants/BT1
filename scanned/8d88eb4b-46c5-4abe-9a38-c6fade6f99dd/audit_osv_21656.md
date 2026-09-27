# [H] CVE-2021-44981

## Summary
Severity: High
Advisory: CVE-2021-44981
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-24
Source: https://osv.dev/vulnerability/CVE-2021-44981
Type: osv

## Details
In QuickBox Pro v2.5.8 and below, the config.php file has a variable which takes a GET parameter value and parses it into a shell_exec(''); function without properly sanitizing any shell arguments, therefore remote code execution is possible. Additionally, as the media server is running as root by default attackers can use the sudo command within this shell_exec(''); function, which allows for privilege escalation by means of RCE.

## References
- https://github.com/QuickBox/QB/issues/202
- https://websec.nl/blog/61b2b37a43a1155c848f3b08/websec%20finds%20critical%20vulnerabilities%20in%20popular%20media%20server
