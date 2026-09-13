# [H] PCSX2 Contains a Stack-based Buffer Overflow in IOP Console Logging

## Summary
Severity: High
Advisory: CVE-2025-49589
Aliases: GHSA-f494-4xf7-xj35
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:N/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-06-12
Source: https://osv.dev/vulnerability/CVE-2025-49589
Type: osv

## Details
PCSX2 is a free and open-source PlayStation 2 (PS2) emulator. A stack-based buffer overflow exists in the Kprintf_HLE function of PCSX2 versions up to 2.3.414. Opening a disc image that logs a specially crafted message may allow a remote attacker to execute arbitrary code if the user enabled IOP Console Logging. This vulnerability is fixed in 2.3.414.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49589.json
- https://github.com/PCSX2/pcsx2/security/advisories/GHSA-f494-4xf7-xj35
- https://nvd.nist.gov/vuln/detail/CVE-2025-49589
- https://github.com/PCSX2/pcsx2/pull/12823
- https://github.com/PCSX2/pcsx2/pull/12826
