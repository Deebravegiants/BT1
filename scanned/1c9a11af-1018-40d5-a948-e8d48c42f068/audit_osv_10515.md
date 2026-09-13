# [H] CVE-2017-16806

## Summary
Severity: High
Advisory: CVE-2017-16806
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2017-16806
Type: osv

## Details
The Process function in RemoteTaskServer/WebServer/HttpServer.cs in Ulterius before 1.9.5.0 allows HTTP server directory traversal.

## References
- https://www.exploit-db.com/exploits/43141/
- https://github.com/Ulterius/server/commit/770d1821de43cf1d0a93c79025995bdd812a76ee
