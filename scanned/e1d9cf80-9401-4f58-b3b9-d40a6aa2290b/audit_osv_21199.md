# [H] CVE-2021-41145

## Summary
Severity: High
Advisory: CVE-2021-41145
Aliases: GHSA-jvpq-23v4-gp3m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-41145
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. FreeSWITCH prior to version 1.10.7 is susceptible to Denial of Service via SIP flooding. When flooding FreeSWITCH with SIP messages, it was observed that after a number of seconds the process was killed by the operating system due to memory exhaustion. By abusing this vulnerability, an attacker is able to crash any FreeSWITCH instance by flooding it with SIP messages, leading to Denial of Service. The attack does not require authentication and can be carried out over UDP, TCP or TLS. This issue was patched in version 1.10.7.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.10.7
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-jvpq-23v4-gp3m
