# [H] CVE-2019-15642

## Summary
Severity: High
Advisory: CVE-2019-15642
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-26
Source: https://osv.dev/vulnerability/CVE-2019-15642
Type: osv

## Details
rpc.cgi in Webmin through 1.920 allows authenticated Remote Code Execution via a crafted object name because unserialise_variable makes an eval call. NOTE: the Webmin_Servers_Index documentation states "RPC can be used to run any command or modify any file on a server, which is why access to it must not be granted to un-trusted Webmin users."

## References
- https://doxfer.webmin.com/Webmin/Webmin_Servers_Index
- https://github.com/webmin/webmin/blob/ab5e00e41ea1ecc1e24b8f8693f3495a0abb1aed/rpc.cgi#L26-L37
- https://github.com/webmin/webmin/commit/df8a43fb4bdc9c858874f72773bcba597ae9432c
- https://www.calypt.com/blog/index.php/authenticated-rce-on-webmin/
