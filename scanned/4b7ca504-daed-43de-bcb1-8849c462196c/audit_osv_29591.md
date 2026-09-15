# [M] CVE-2024-44843

## Summary
Severity: Medium
Advisory: CVE-2024-44843
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:L)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2024-44843
Type: osv

## Details
An issue in the web socket handshake process of SteVe v3.7.1 allows attackers to bypass authentication and execute arbitrary coammands via supplying crafted OCPP requests.

## References
- https://gist.github.com/Badranh/94359664799db6d4709871f0c353f476
- https://github.com/steve-community/steve/blob/master/src/main/java/de/rwth/idsg/steve/ocpp/ws/OcppWebSocketHandshakeHandler.java
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44843.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44843
- https://github.com/steve-community/steve/issues/1546
