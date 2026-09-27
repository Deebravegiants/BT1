# [C] Ground Station: Unauthenticated arbitrary file write (path traversal) in save-waterfall-snapshot leads to remote code execution

## Summary
Severity: Critical
Advisory: CVE-2026-53451
Aliases: GHSA-q35x-w3h6-36w8
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-53451
Type: osv

## Details
Ground Station is a browser-based suite for satellite tracking, SDR reception, hardware control, and telemetry decoding. Prior to version 0.4.13, the unauthenticated save-waterfall-snapshot Socket.IO command passes attacker-controlled snapshotName input from backend/handlers/entities/sdr.py to backend/server/snapshots.py, where os.path.join permits an absolute path or parent-directory traversal and writes attacker-controlled base64-decoded bytes outside backend/data/snapshots. An attacker can write a logging YAML file containing a logging.config.dictConfig callable factory, use the unauthenticated update-app-config operation to set log_config to that file, and invoke restart_service. During restart, backend/common/logger.py passes the YAML through resolve_log_config_path(), yaml.safe_load(), and logging.config.dictConfig(), which executes the factory with service privileges and can also cause a persistent crash loop. This issue is fixed in version 0.4.13.

## References
- https://github.com/sgoudelis/ground-station/releases/tag/v0.4.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53451.json
- https://github.com/sgoudelis/ground-station/security/advisories/GHSA-q35x-w3h6-36w8
- https://nvd.nist.gov/vuln/detail/CVE-2026-53451
- https://github.com/sgoudelis/ground-station/commit/5649905f1021155933463a54a76030924adffb9d
