# [M] Privilege escalation to the `CAP_NET_RAW` capability via the `programs.captive-browser` NixOS module

## Summary
Severity: Medium
Advisory: CVE-2026-25740
Aliases: GHSA-wc3r-c66x-8xmc
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25740
Type: osv

## Details
captive browser, a dedicated Chrome instance to log into captive portals without messing with DNS settings. In 25.05 and earlier, when programs.captive-browser is enabled, any user of the system can run arbitrary commands with the CAP_NET_RAW capability (binding to privileged ports, spoofing localhost traffic from privileged services...). This vulnerability is fixed in 25.11 and 26.05.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25740.json
- https://github.com/NixOS/nixpkgs/security/advisories/GHSA-wc3r-c66x-8xmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-25740
- https://github.com/NixOS/nixpkgs/pull/487775
- https://github.com/NixOS/nixpkgs/pull/487779
