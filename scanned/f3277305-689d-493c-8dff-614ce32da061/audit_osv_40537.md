# [M] Ground Station: Unauthenticated out-of-containment file read via `sigmfplayback` `recordingPath`

## Summary
Severity: Medium
Advisory: CVE-2026-53452
Aliases: GHSA-g344-jqcx-cr7q
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-53452
Type: osv

## Details
Ground Station is a browser-based suite for satellite tracking, SDR reception, hardware control, and telemetry decoding. Prior to version 0.4.13, the unauthenticated configure-sdr Socket.IO command accepts a recordingPath for the sigmf-playback SDR and backend/handlers/entities/sdr.py stores it without validation before backend/hardware/sigmfprobe.py opens the path without enforcing containment. An absolute path or parent-directory escape ending in .sigmf-meta is parsed as JSON and returned in reply["data"]["metadata"] by the get-sdr-parameters flow. Exploitation requires the metadata file to be readable JSON and to have a sibling .sigmf-data file, but it can disclose contents outside backend/data/recordings without authentication. This issue is fixed in version 0.4.13.

## References
- https://github.com/sgoudelis/ground-station/releases/tag/v0.4.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53452.json
- https://github.com/sgoudelis/ground-station/security/advisories/GHSA-g344-jqcx-cr7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-53452
- https://github.com/sgoudelis/ground-station/commit/5649905f1021155933463a54a76030924adffb9d
