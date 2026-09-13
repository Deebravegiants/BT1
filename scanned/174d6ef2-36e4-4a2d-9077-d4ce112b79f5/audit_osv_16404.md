# [H] CVE-2019-6475

## Summary
Severity: High
Advisory: CVE-2019-6475
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-10-17
Source: https://osv.dev/vulnerability/CVE-2019-6475
Type: osv

## Details
Mirror zones are a BIND feature allowing recursive servers to pre-cache zone data provided by other servers. A mirror zone is similar to a zone of type secondary, except that its data is subject to DNSSEC validation before being used in answers, as if it had been looked up via traditional recursion, and when mirror zone data cannot be validated, BIND falls back to using traditional recursion instead of the mirror zone. However, an error in the validity checks for the incoming zone data can allow an on-path attacker to replace zone data that was validated with a configured trust anchor with forged data of the attacker's choosing. The mirror zone feature is most often used to serve a local copy of the root zone. If an attacker was able to insert themselves into the network path between a recursive server using a mirror zone and a root name server, this vulnerability could then be used to cause the recursive server to accept a copy of falsified root zone data. This affects BIND versions 9.14.0 up to 9.14.6, and 9.15.0 up to 9.15.4.

## References
- https://support.f5.com/csp/article/K42238532?utm_source=f5support&amp%3Butm_medium=RSS
- https://kb.isc.org/docs/cve-2019-6475
- https://security.netapp.com/advisory/ntap-20191024-0004/
