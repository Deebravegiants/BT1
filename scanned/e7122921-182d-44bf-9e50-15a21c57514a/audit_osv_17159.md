# [M] CVE-2020-13152

## Summary
Severity: Medium
Advisory: CVE-2020-13152
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-05-20
Source: https://osv.dev/vulnerability/CVE-2020-13152
Type: osv

## Details
A remote user can create a specially crafted M3U file, media playlist file that when loaded by the target user, will trigger a memory leak, whereby Amarok 2.8.0 continue to waste resources over time, eventually allows attackers to cause a denial of service.

## References
- http://packetstormsecurity.com/files/159898/Amarok-2.8.0-Denial-Of-Service.html
- https://r00texpl0it.wordpress.com/2020/05/20/kde-amarok-2-8-0-allows-remote-attackers-to-cause-a-denial-of-service/
