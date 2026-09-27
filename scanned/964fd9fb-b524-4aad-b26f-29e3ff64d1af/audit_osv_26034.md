# [H] Asterisk susceptible to Denial of Service via DTLS Hello packets during call initiation

## Summary
Severity: High
Advisory: CVE-2023-49786
Aliases: GHSA-hxj9-xwr8-w8pq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-49786
Type: osv

## Details
Asterisk is an open source private branch exchange and telephony toolkit. In Asterisk prior to versions 18.20.1, 20.5.1, and 21.0.1; as well as certified-asterisk prior to 18.9-cert6; Asterisk is susceptible to a DoS due to a race condition in the hello handshake phase of the DTLS protocol when handling DTLS-SRTP for media setup. This attack can be done continuously, thus denying new DTLS-SRTP encrypted calls during the attack. Abuse of this vulnerability may lead to a massive Denial of Service on vulnerable Asterisk servers for calls that rely on DTLS-SRTP. Commit d7d7764cb07c8a1872804321302ef93bf62cba05 contains a fix, which is part of versions 18.20.1, 20.5.1, 21.0.1, amd 18.9-cert6.

## References
- http://packetstormsecurity.com/files/176251/Asterisk-20.1.0-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2023/Dec/24
- http://www.openwall.com/lists/oss-security/2023/12/15/7
- https://lists.debian.org/debian-lts-announce/2023/12/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49786.json
- https://github.com/EnableSecurity/advisories/tree/master/ES2023-01-asterisk-dtls-hello-race
- https://github.com/asterisk/asterisk/security/advisories/GHSA-hxj9-xwr8-w8pq
- https://nvd.nist.gov/vuln/detail/CVE-2023-49786
- https://github.com/asterisk/asterisk/commit/d7d7764cb07c8a1872804321302ef93bf62cba05
