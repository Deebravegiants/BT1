# [C] CVE-2021-25981

## Summary
Severity: Critical
Advisory: CVE-2021-25981
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-03
Source: https://osv.dev/vulnerability/CVE-2021-25981
Type: osv

## Details
In Talkyard, regular versions v0.2021.20 through v0.2021.33 and dev versions v0.2021.20 through v0.2021.34, are vulnerable to Insufficient Session Expiration. This may allow an attacker to reuse the admin’s still-valid session token even when logged-out, to gain admin privileges, given the attacker is able to obtain that token (via other, hypothetical attacks)

## References
- https://github.com/debiki/talkyard/commit/b0310df019887f3464895529c773bc7d85ddcf34
- https://github.com/debiki/talkyard/commit/b0712915d8a22a20b09a129924e8a29c25ae5761
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25981
