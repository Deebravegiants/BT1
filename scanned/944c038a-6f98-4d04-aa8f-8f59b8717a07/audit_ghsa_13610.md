# [H] MTProto proxy remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-738q-mc72-2q22
CVE: CVE-2023-45312
CWE: CWE-1188, CWE-94
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-738q-mc72-2q22
Type: github-advisory

## Affected
- Hex: `mtproto_proxy` — affected >=0

## Details
In the mtproto_proxy (aka MTProto proxy) component through 0.7.2 for Erlang, a low-privileged remote attacker can access an improperly secured default installation without authenticating and achieve remote command execution ability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45312
- https://github.com/seriyps/mtproto_proxy
- https://medium.com/@_sadshade/almost-2000-telegram-proxy-servers-are-potentially-vulnerable-to-rce-since-2018-742a455be16b
