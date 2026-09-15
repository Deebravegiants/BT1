# [M] CVE-2026-80213

## Summary
Severity: Medium
Advisory: CVE-2026-80213
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-80213
Type: osv

## Details
An issue was discovered in the resolv gem before 0.7.2 for Ruby. Resolv::DNS::MessageEncoder wrote a DNS label's length into a single octet without checking its range. A label longer than 255 octets had its length stored modulo 256 but the label data was written unchanged, and thus the bytes on the wire described a different name than the one the application asked to encode. RFC 1035 section 2.3.4 limits a label to 63 octets, and the two high bits of the length octet are reserved for compression pointers. put_string packed the length with put_pack("C", d.length) and put_label used it for labels, and thus any value from 0 to 255 could end up as a label length octet, including the reserved 0x40-0xBF range and the 0xC0-0xFF pointer range. Resolv::DNS::Name.create did not check per-label or total name length either, and thus an attacker-controlled hostname reached the encoder unchanged. An application that resolves an attacker-controlled hostname sends a query whose wire bytes name a domain the attacker chose. A hostname suffix that the application validates against an allowlist becomes padding that never appears on the wire, and thus allowlist and egress checks can be bypassed. The recursive resolver caches the response under the attacker's name, and DNS logs record that name rather than the one the application asked for. A label length whose low octet lands in the 0xC0-0xFF range produces a length octet that conforming parsers read as the start of a compression pointer, with the following attacker-controlled byte as the offset.

## References
- https://www.ruby-lang.org/en/news/2026/08/27/multiple-vulnerabilities-in-resolv/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80213.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80213
- https://github.com/ruby/resolv
