# [H] CVE-2017-12778

## Summary
Severity: High
Advisory: CVE-2017-12778
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-05-09
Source: https://osv.dev/vulnerability/CVE-2017-12778
Type: osv

## Details
The UI Lock feature in qBittorrent version 3.3.15 is vulnerable to Authentication Bypass, which allows Attack to gain unauthorized access to qBittorrent functions by tampering the affected flag value of the config file at the C:\Users\<username>\Roaming\qBittorrent pathname. The attacker must change the value of the "locked" attribute to "false" within the "Locking" stanza. NOTE: This is an intended behavior. See https://github.com/qbittorrent/qBittorrent/wiki/I-forgot-my-UI-lock-password

## References
- https://github.com/qbittorrent/qBittorrent/wiki/I-forgot-my-UI-lock-password
- https://medium.com/%40BaYinMin/cve-2017-12778-qbittorrent-ui-lock-authentication-bypass-30959ff55ada
- http://archive.is/eF2GR
