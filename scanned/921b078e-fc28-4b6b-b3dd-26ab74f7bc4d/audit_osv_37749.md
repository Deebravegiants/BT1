# [M] Frigate has SSRF vulnerability in /ffprobe endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-33126
Aliases: GHSA-j6g3-3j3q-c2xv
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33126
Type: osv

## Details
Frigate is a network video recorder (NVR) with realtime local object detection for IP cameras. Prior to version 0.16.3, the /ffprobe endpoint accepts arbitrary user-controlled URLs without proper validation, allowing Server-Side Request Forgery (SSRF) attacks. An attacker can use the Frigate server to make HTTP requests to internal network resources, cloud metadata services, or perform port scanning. This issue has been patched in version 0.16.3.

## References
- https://github.com/blakeblackshear/frigate/releases/tag/v0.16.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33126.json
- https://github.com/blakeblackshear/frigate/security/advisories/GHSA-j6g3-3j3q-c2xv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33126
