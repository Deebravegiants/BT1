# [C] EVerest has an integer overflow in the "v2g_incoming_v2gtp" function

## Summary
Severity: Critical
Advisory: CVE-2024-37310
Aliases: GHSA-8g9q-7qr9-vc96
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-10
Source: https://osv.dev/vulnerability/CVE-2024-37310
Type: osv

## Details
EVerest is an EV charging software stack. An integer overflow in the "v2g_incoming_v2gtp" function in the v2g_server.cpp implementation can allow a remote attacker to overflow the process' heap. This vulnerability is fixed in 2024.3.1 and 2024.6.0.

## References
- https://github.com/EVerest/everest-core/releases/tag/2024.3.1
- https://github.com/EVerest/everest-core/releases/tag/2024.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37310.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-8g9q-7qr9-vc96
- https://nvd.nist.gov/vuln/detail/CVE-2024-37310
- https://github.com/EVerest/everest-core/commit/f73620c4c0f626e1097068a47e10cc27b369ad8e
- https://plaxidityx.com/blog/automotive-cyber-security/ev-cyber-security-plaxidityx-discovers-critical-vulnerability-in-everest-open-source-ev-charging-firmware-stack-cve-2024-37310/
