# [M] Lego does not enforce HTTPS

## Summary
Severity: Medium
Advisory: CVE-2025-54799
Aliases: GHSA-q82r-2j7m-9rv4, GO-2025-3847
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/CVE-2025-54799
Type: osv

## Details
Let's Encrypt client and ACME library written in Go (Lego). In versions 4.25.1 and below, the github.com/go-acme/lego/v4/acme/api package (thus the lego library and the lego cli as well) don't enforce HTTPS when talking to CAs as an ACME client. Unlike the http-01 challenge which solves an ACME challenge over unencrypted HTTP, the ACME protocol requires HTTPS when a client communicates with the CA to performs ACME functions. However, the library fails to enforce HTTPS both in the original discover URL (configured by the library user) and in the subsequent addresses returned by the CAs in the directory and order objects. If users input HTTP URLs or CAs misconfigure endpoints, protocol operations occur over HTTP instead of HTTPS. This compromises privacy by exposing request/response details like account and request identifiers to network attackers. This was fixed in version 4.25.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54799.json
- https://github.com/go-acme/lego/security/advisories/GHSA-q82r-2j7m-9rv4
- https://nvd.nist.gov/vuln/detail/CVE-2025-54799
- https://github.com/go-acme/lego/commit/238454b5f74f3cfcbb244ff0d0dc914a4ad44b96
