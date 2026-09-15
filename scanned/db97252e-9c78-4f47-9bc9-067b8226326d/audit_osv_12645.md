# [M] CVE-2018-13878

## Summary
Severity: Medium
Advisory: CVE-2018-13878
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-07-11
Source: https://osv.dev/vulnerability/CVE-2018-13878
Type: osv

## Details
An XSS issue was discovered in packages/rocketchat-mentions/Mentions.js in Rocket.Chat before 0.65. The real name of a username is displayed unescaped when the user is mentioned (using the @ symbol) in a channel or private chat. Consequently, it is possible to exfiltrate the secret token of every user and also admins in the channel.

## References
- https://github.com/RocketChat/Rocket.Chat/pull/10793
