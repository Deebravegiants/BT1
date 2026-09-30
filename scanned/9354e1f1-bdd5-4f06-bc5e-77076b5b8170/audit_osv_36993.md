# [H] RIOT has an Out-of-Bounds Write in nanoCoAP Handler

## Summary
Severity: High
Advisory: CVE-2026-27703
Aliases: GHSA-qgj4-9jff-93cj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-27703
Type: osv

## Details
RIOT is an open-source microcontroller operating system, designed to match the requirements of Internet of Things (IoT) devices and other embedded devices. In 2026.01 and earlier, the default handler for the well_known_core resource coap_well_known_core_default_handler writes user-provided option data and other data into a fixed size buffer without validating the buffer is large enough to contain the response. This vulnerability allows an attacker to corrupt neighboring stack location, including security-sensitive addresses like the return address, leading to denial of service or arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27703.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-qgj4-9jff-93cj
- https://nvd.nist.gov/vuln/detail/CVE-2026-27703
