# [H] Erlang Solutions MongooseIM vulnerable to denial of service (DoS) via crafted XMPP stream

## Summary
Severity: High
Advisory: GHSA-5v5w-44w6-q5hv
CVE: CVE-2014-2829
CWE: CWE-770
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5v5w-44w6-q5hv
Type: github-advisory

## Affected
- Hex: `MongooseIM` — affected >=0 <1.3.2

## Details
Erlang Solutions MongooseIM through 1.3.1 rev. 2 does not properly restrict the processing of compressed XML elements, which allows remote attackers to cause a denial of service (resource consumption) via a crafted XMPP stream, aka an "xmppbomb" attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2829
- https://github.com/esl/MongooseIM/commit/586d96cc12ef218243a3466354b4d208b5472a6c
- https://github.com/esl/MongooseIM
- http://xmpp.org/resources/security-notices/uncontrolled-resource-consumption-with-highly-compressed-xmpp-stanzas
