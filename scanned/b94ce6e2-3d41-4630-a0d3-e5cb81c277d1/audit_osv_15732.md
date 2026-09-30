# [M] CVE-2019-19251

## Summary
Severity: Medium
Advisory: CVE-2019-19251
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-12-10
Source: https://osv.dev/vulnerability/CVE-2019-19251
Type: osv

## Details
The Last.fm desktop app (Last.fm Scrobbler) through 2.1.39 on macOS makes HTTP requests that include an API key without the use of SSL/TLS. Although there is an Enable SSL option, it is disabled by default, and cleartext requests are made as soon as the app starts.

## References
- https://getsatisfaction.com/lastfm/topics/why-doesnt-the-macos-client-enable-ssl-by-default-c1nh5k1s054ak
