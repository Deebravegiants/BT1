# [H] CVE-2025-3875

## Summary
Severity: High
Advisory: CVE-2025-3875
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-3875
Type: osv

## Details
Thunderbird parses addresses in a way that can allow sender spoofing in case the server allows an invalid From address to be used. For example, if the From header contains an (invalid) value "Spoofed Name  ", Thunderbird treats spoofed@example.com as the actual address. This vulnerability affects Thunderbird < 128.10.1 and Thunderbird < 138.0.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00022.html
- https://www.mozilla.org/security/advisories/mfsa2025-34/
- https://www.mozilla.org/security/advisories/mfsa2025-35/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1950629
