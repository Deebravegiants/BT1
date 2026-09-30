# [H] Frigate Vulnerable to Arbitrary File Read via Export Thumbnail "image_path" parameter

## Summary
Severity: High
Advisory: CVE-2025-62382
Aliases: GHSA-8gv4-5jr9-v96j
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-62382
Type: osv

## Details
Frigate is a network video recorder (NVR) with realtime local object detection for IP cameras. Prior to 0.16.2, Frigate's export workflow allows an authenticated operator to nominate any filesystem location as the thumbnail source for a video export. Because that path is copied verbatim into the publicly served clips directory, the feature can be abused to read arbitrary files that reside on the host running Frigate. In practice, a low-privilege user with API access can pivot from viewing camera footage to exfiltrating sensitive configuration files, secrets, or user data from the appliance itself. This behavior violates the principle of least privilege for the export subsystem and turns a convenience feature into a direct information disclosure vector, with exploitation hinging on a short race window while the background exporter copies the chosen file into place before cleanup runs. This vulnerability is fixed in 0.16.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62382.json
- https://github.com/blakeblackshear/frigate/security/advisories/GHSA-8gv4-5jr9-v96j
- https://nvd.nist.gov/vuln/detail/CVE-2025-62382
- https://github.com/blakeblackshear/frigate/commit/d7f7cd7be16bfe7a12766b797da6b8add687ccd9
