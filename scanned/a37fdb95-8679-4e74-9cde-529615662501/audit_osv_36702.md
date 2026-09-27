# [M] RIOT Vulnerable to Multiple Out-of-Bounds Read When Processing Received 6LoWPAN SFR Fragments

## Summary
Severity: Medium
Advisory: CVE-2026-25139
Aliases: GHSA-c8fh-23qr-97mc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25139
Type: osv

## Details
RIOT is an open-source microcontroller operating system, designed to match the requirements of Internet of Things (IoT) devices and other embedded devices. In version 2025.10 and prior, multiple out-of-bounds read allow any unauthenticated user, with ability to send or manipulate input packets, to read adjacent memory locations, or crash a vulnerable device running the 6LoWPAN stack. The received packet is cast into a sixlowpan_sfr_rfrag_t struct and dereferenced without validating the packet is large enough to contain the struct object. At time of publication, no known patch exists.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25139.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-c8fh-23qr-97mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-25139
