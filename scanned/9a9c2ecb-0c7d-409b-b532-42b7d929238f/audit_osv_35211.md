# [M] free5GC has Array Index Out of Bounds in AMF Leading to Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2025-69248
Aliases: GHSA-h6xc-8vvf-jcjp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/CVE-2025-69248
Type: osv

## Details
free5GC is an open-source project for 5th generation (5G) mobile core networks. Versions up to and including 1.4.1 of free5GC's AMF service have a Buffer Overflow vulnerability leading to Denial of Service. Remote unauthenticated attackers can crash the AMF service by sending a specially crafted NAS Registration Request with a malformed 5GS Mobile Identity, causing complete denial of service for the 5G core network. All deployments of free5GC using the AMF component may be affected. Pull request 43 of the free5gc/nas repo contains a fix. No direct workaround is available at the application level. Applying the official patch is recommended.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69248.json
- https://github.com/free5gc/free5gc/security/advisories/GHSA-h6xc-8vvf-jcjp
- https://nvd.nist.gov/vuln/detail/CVE-2025-69248
- https://github.com/free5gc/free5gc/issues/747
- https://github.com/free5gc/nas/commit/0329a7ac3f314f210366c1b3c33dc29eded4ac5f
- https://github.com/free5gc/nas/pull/43
