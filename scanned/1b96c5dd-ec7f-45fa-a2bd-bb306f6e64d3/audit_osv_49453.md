# [M] CVE-2019-12383

## Summary
Severity: Medium
Advisory: CVE-2019-12383
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2019-05-28
Source: https://osv.dev/vulnerability/CVE-2019-12383
Type: osv

## Details
Tor Browser before 8.0.1 has an information exposure vulnerability. It allows remote attackers to detect the browser's UI locale by measuring a button width, even if the user has a "Don't send my language" setting.

## References
- http://www.securityfocus.com/bid/108484
- https://trac.torproject.org/projects/tor/ticket/24056
- https://hackerone.com/reports/282748
- https://gitweb.torproject.org/tor-browser.git/commit/?id=cbb04b72c68272c2de42f157d40cd7d29a6b7b55
