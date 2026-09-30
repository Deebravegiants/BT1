# [H] CVE-2016-10579

## Summary
Severity: High
Advisory: CVE-2016-10579
Aliases: GHSA-jh5w-6964-x5cf
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-01
Source: https://osv.dev/vulnerability/CVE-2016-10579
Type: osv

## Details
Chromedriver is an NPM wrapper for selenium ChromeDriver. Chromedriver before 2.26.1 downloads binary resources over HTTP, which leaves it vulnerable to MITM attacks. It may be possible to cause remote code execution (RCE) by swapping out the requested binary with an attacker controlled binary if the attacker is on the network or positioned in between the user and the remote server.

## References
- https://nodesecurity.io/advisories/160
