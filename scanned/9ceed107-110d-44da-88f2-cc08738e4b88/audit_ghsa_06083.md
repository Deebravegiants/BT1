# [M] Froxlor DomainZones.add allows DNS zone-file RR injection via record/type fields

## Summary
Severity: Medium
Advisory: GHSA-5rw4-4665-cvwf
CVE: CVE-2026-54543
CWE: CWE-20, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-5rw4-4665-cvwf
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.8

## Details
Froxlor's DomainZones.add API command accepts user-controlled DNS record and type values and later writes them into generated BIND zone files without rejecting line delimiters, tab characters, or zone-file comment delimiters.

The stronger variant is in record. An authenticated customer with DNS-zone permissions can submit a normal A record request where record is:

www\t60\tIN\tA\t6.6.6.6 ;\n@

with type=A and content=127.0.0.1. The current record flow trims/lower-cases/IDNA-encodes the value, but does not reject CR/LF/HTAB or semicolon. The real Froxlor\Dns\DnsEntry::__toString() sink renders it as:

www    60    in    a    6.6.6.6 ;
@      18000 IN    A    127.0.0.1

BIND accepts the generated zone file:

named-checkzone example.com froxlor_dns_record_injected.zone
zone example.com/IN: loaded serial 2026060501
OK

named-compilezone -D confirms both records are parsed as real DNS RRs:

example.com.       18000 IN A 127.0.0.1
www.example.com.      60 IN A 6.6.6.6
zone example.com/IN: loaded serial 2026060501
OK

Affected code in 2.3.7:
- lib/Froxlor/Api/Commands/DomainZones.php:92-93 reads record/type from API params.
- lib/Froxlor/Api/Commands/DomainZones.php:122-136 trims/lower-cases/IDNA-encodes record without control-character rejection.
- lib/Froxlor/Api/Commands/DomainZones.php:157-160 hardens content only.
- lib/Froxlor/Api/Commands/DomainZones.php:314-321 and 347-357 store record/type/content into domain_dns_entries.
- lib/Froxlor/Dns/Dns.php:297 passes stored values to DnsEntry.
- lib/Froxlor/Dns/DnsEntry.php:83 concatenates record/type/content into a zone-file line.

There is also a related type-field variant because type is not allowlisted and domain_dns_entries.type is varchar(10). The value NS\tns.\n@\tA renders one submitted entry as multiple zone-file records.

Impact: authenticated customer with DNS-zone permissions can inject additional BIND resource-record lines into the generated zone file for a domain they can manage in Froxlor, bypassing Froxlor's DNS field-level validation. This is DNS zone integrity loss and possible DNS availability impact inside the caller's manageable zone.

Suggested remediation: allowlist DNS RR types, reject CR/LF/HTAB/control chars/spaces/semicolon in record and type, validate record as a DNS owner name while allowing intended cases such as @, *, *.label, _service._proto, _dmarc, and DKIM selectors. Add defense-in-depth in DnsEntry or the DNS serializer so CR/LF cannot reach generated zone lines.

Attribution: Yaohui Wang.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-5rw4-4665-cvwf
- https://github.com/froxlor/froxlor/commit/a4f09f09fa71337b6cdff364d0a641d631a0130a
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.8
