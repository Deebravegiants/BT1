# [H] FreeSWITCH allows authorized users to cause a denial of service attack by sending re-INVITE with SDP containing duplicate codec names

## Summary
Severity: High
Advisory: CVE-2023-40019
Aliases: GHSA-gjj5-79p2-9g3q
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-15
Source: https://osv.dev/vulnerability/CVE-2023-40019
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.10.10, FreeSWITCH allows authorized users to cause a denial of service attack by sending re-INVITE with SDP containing duplicate codec names. When a call in FreeSWITCH completes codec negotiation, the `codec_string` channel variable is set with the result of the negotiation. On a subsequent re-negotiation, if an SDP is offered that contains codecs with the same names but with different formats, there may be too many codec matches detected by FreeSWITCH leading to overflows of its internal arrays. By abusing this vulnerability, an attacker is able to corrupt stack of FreeSWITCH leading to an undefined behavior of the system or simply crash it. Version 1.10.10 contains a patch for this issue.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.10.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40019.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-gjj5-79p2-9g3q
- https://nvd.nist.gov/vuln/detail/CVE-2023-40019
