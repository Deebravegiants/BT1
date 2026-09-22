# [H] CVE-2019-15752

## Summary
Severity: High
Advisory: CVE-2019-15752
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-28
Source: https://osv.dev/vulnerability/CVE-2019-15752
Type: osv

## Details
Docker Desktop Community Edition before 2.1.0.1 allows local users to gain privileges by placing a Trojan horse docker-credential-wincred.exe file in %PROGRAMDATA%\DockerDesktop\version-bin\ as a low-privilege user, and then waiting for an admin or service user to authenticate with Docker, restart Docker, or run 'docker login' to force the command.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-15752
- https://lists.apache.org/thread.html/rf1bbc0ea4a9f014cf94df9a12a6477d24a27f52741dbc87f2fd52ff2%40%3Cissues.geode.apache.org%3E
- http://packetstormsecurity.com/files/157404/Docker-Credential-Wincred.exe-Privilege-Escalation.html
- https://medium.com/%40morgan.henry.roman/elevation-of-privilege-in-docker-for-windows-2fd8450b478e
