# [C] Net::Statsite::Client versions through 1.1.0 for Perl allow metric injections

## Summary
Severity: Critical
Advisory: CVE-2026-11373
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-11373
Type: osv

## Details
Net::Statsite::Client versions through 1.1.0 for Perl allow metric injections.

Net::Statsite::Client is a client for the statsite protocol, which is a variant of statsd.

Newlines are not removed from metric names, allowing metric injections.

Values are not sanitised for newlines or other protocol control characters such as colons or pipes, allowing metric injections.

## References
- https://cpan.org/modules
- https://metacpan.org/release/JASEI/Net-Statsite-Client-1.1.0/view/lib/Net/Statsite/Client.pm
- https://www.cve.org/CVERecord?id=CVE-2026-46719
- https://www.cve.org/CVERecord?id=CVE-2026-46720
- https://www.cve.org/CVERecord?id=CVE-2026-46739
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11373
- https://security.metacpan.org/patches/N/Net-Statsite-Client/1.1.0/CVE-2026-11373-r1.patch
- https://github.com/avast/Net-Statsite-Client
- http://armon.github.io/statsite
