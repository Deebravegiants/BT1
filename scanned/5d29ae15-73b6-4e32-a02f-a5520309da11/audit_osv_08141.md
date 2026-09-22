# [H] CVE-2016-10605

## Summary
Severity: High
Advisory: CVE-2016-10605
Aliases: GHSA-65q2-x652-xx84
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-01
Source: https://osv.dev/vulnerability/CVE-2016-10605
Type: osv

## Details
dalek-browser-ie is Internet Explorer bindings for DalekJS. dalek-browser-ie downloads binary resources over HTTP, which leaves it vulnerable to MITM attacks. It may be possible to cause remote code execution (RCE) by swapping out the requested binary with an attacker controlled binary if the attacker is on the network or positioned in between the user and the remote server.

## References
- https://nodesecurity.io/advisories/209
