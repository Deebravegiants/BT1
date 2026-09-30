# [M] EVerest affected by memory exhaustion in libocpp

## Summary
Severity: Medium
Advisory: CVE-2025-68138
Aliases: GHSA-f8c2-44c3-7v55
CVSS: 4.7 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-68138
Type: osv

## Details
EVerest is an EV charging software stack, and EVerest libocpp is a C++ implementation of the Open Charge Point Protocol. In libocpp prior to version 0.30.1, pointers returned by the `strdup` calls are never freed. At each connection attempt, the newly allocated memory area will be leaked, potentially causing memory exhaustion and denial of service. Version 0.30.1 fixes the issue.

## References
- https://github.com/EVerest/libocpp/blob/89c7b62ec899db637f43b54f19af2c4af30cfa66/lib/ocpp/common/websocket/websocket_libwebsockets.cpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68138.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-f8c2-44c3-7v55
- https://nvd.nist.gov/vuln/detail/CVE-2025-68138
