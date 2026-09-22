# [H] Asterisk's PJSIP_HEADER dialplan function can overwrite memory/cause crash when using 'update'

## Summary
Severity: High
Advisory: CVE-2023-37457
Aliases: GHSA-98rc-4j27-74hh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-37457
Type: osv

## Details
Asterisk is an open source private branch exchange and telephony toolkit. In Asterisk versions 18.20.0 and prior, 20.5.0 and prior, and 21.0.0; as well as ceritifed-asterisk 18.9-cert5 and prior, the 'update' functionality of the PJSIP_HEADER dialplan function can exceed the available buffer space for storing the new value of a header. By doing so this can overwrite memory or cause a crash. This is not externally exploitable, unless dialplan is explicitly written to update a header based on data from an outside source. If the 'update' functionality is not used the vulnerability does not occur. A patch is available at commit a1ca0268254374b515fa5992f01340f7717113fa.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37457.json
- https://github.com/asterisk/asterisk/security/advisories/GHSA-98rc-4j27-74hh
- https://nvd.nist.gov/vuln/detail/CVE-2023-37457
- https://github.com/asterisk/asterisk/commit/a1ca0268254374b515fa5992f01340f7717113fa
