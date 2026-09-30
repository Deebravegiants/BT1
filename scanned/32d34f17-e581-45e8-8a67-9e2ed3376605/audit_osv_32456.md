# [C] Bruno ignores Safe-Mode in Asserts expressions

## Summary
Severity: Critical
Advisory: CVE-2025-30354
Aliases: GHSA-hffg-7v8v-79j3
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-30354
Type: osv

## Details
Bruno is an open source IDE for exploring and testing APIs. A bug in the assertion runtime caused assert expressions to run in Developer Mode, even if Safe Mode was selected. The bug resulted in the sandbox settings to be ignored for the particular case where a single request is run/sent. This vulnerability's attack surface is limited strictly to scenarios where users import collections from untrusted or malicious sources. The exploit requires deliberate action from the user—specifically, downloading and opening an externally provided malicious Bruno collection. The vulnerability is fixed in 1.39.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30354.json
- https://github.com/usebruno/bruno/security/advisories/GHSA-hffg-7v8v-79j3
- https://nvd.nist.gov/vuln/detail/CVE-2025-30354
