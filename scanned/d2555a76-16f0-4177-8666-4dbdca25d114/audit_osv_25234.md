# [H] heap-over-flow and integer-overflow in sofia-sip

## Summary
Severity: High
Advisory: CVE-2023-32307
Aliases: GHSA-rm4c-ccvf-ff9c
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-32307
Type: osv

## Details
Sofia-SIP is an open-source SIP User-Agent library, compliant with the IETF RFC3261 specification.
Referring to [GHSA-8599-x7rq-fr54](https://github.com/freeswitch/sofia-sip/security/advisories/GHSA-8599-x7rq-fr54), several other potential heap-over-flow and integer-overflow in stun_parse_attr_error_code and stun_parse_attr_uint32 were found because the lack of attributes length check when Sofia-SIP handles STUN packets. The previous patch of [GHSA-8599-x7rq-fr54](https://github.com/freeswitch/sofia-sip/security/advisories/GHSA-8599-x7rq-fr54) fixed the vulnerability when attr_type did not match the enum value, but there are also vulnerabilities in the handling of other valid cases. The OOB read and integer-overflow made by attacker may lead to crash, high consumption of memory or even other more serious consequences. These issue have been addressed in version 1.13.15. Users are advised to upgrade.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OY66DOQ3B7GULJTI66X5HNX5FU3P65CX/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32307.json
- https://github.com/freeswitch/sofia-sip/security/advisories/GHSA-rm4c-ccvf-ff9c
- https://nvd.nist.gov/vuln/detail/CVE-2023-32307
- https://www.debian.org/security/2023/dsa-5431
