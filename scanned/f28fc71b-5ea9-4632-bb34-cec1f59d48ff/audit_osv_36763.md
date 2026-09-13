# [C] Frigate Affected by Authenticated Remote Command Execution (RCE) and Container Escape

## Summary
Severity: Critical
Advisory: CVE-2026-25643
Aliases: GHSA-4c97-5jmr-8f6x
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-25643
Type: osv

## Details
Frigate is a network video recorder (NVR) with realtime local object detection for IP cameras. Prior to 0.16.4, a critical Remote Command Execution (RCE) vulnerability has been identified in the Frigate integration with go2rtc. The application does not sanitize user input in the video stream configuration (config.yaml), allowing direct injection of system commands via the exec: directive. The go2rtc service executes these commands without restrictions. This vulnerability is only exploitable by an administrator or users who have exposed their Frigate install to the open internet with no authentication which allows anyone full administrative control. This vulnerability is fixed in 0.16.4.

## References
- https://github.com/blakeblackshear/frigate/releases/tag/v0.16.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25643.json
- https://github.com/blakeblackshear/frigate/security/advisories/GHSA-4c97-5jmr-8f6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-25643
