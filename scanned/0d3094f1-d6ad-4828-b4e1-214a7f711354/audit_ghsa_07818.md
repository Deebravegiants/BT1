# [M] EVE's Debug Functions Unlockable Without Triggering Measured Boot

## Summary
Severity: Medium
Advisory: GHSA-4c4v-42hc-72p6
CVE: CVE-2023-43633
CWE: CWE-522, CWE-922
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-4c4v-42hc-72p6
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/eve` — affected >=0 <0.0.0-20220708121648-5fef4d92e758

## Details
### Impact

On boot, Pillar checks for /config/GlobalConfig/global.json and overrides system configuration if present. This allows enabling debug functions like SSH (debug.enable.ssh), USB keyboard (debug.enable.usb), and VNC access (app.allow.vnc) without triggering the measured boot. Thus, a user with physical access can take out the disk and modify the content of this file in the /config partition and then re-insert the disk.

### Patches

Fixed in ​​10.1.0 and 9.4.3-lts

### Workarounds

None

## References
- https://github.com/lf-edge/eve/security/advisories/GHSA-4c4v-42hc-72p6
- https://nvd.nist.gov/vuln/detail/CVE-2023-43633
- https://github.com/lf-edge/eve/commit/5fef4d92e75838cc78010edaed5247dfbdae1889
- https://github.com/lf-edge/eve/commit/aa3501d6c57206ced222c33aea15a9169d629141
- https://asrg.io/security-advisories/cve-2023-43633
- https://asrg.io/security-advisories/debug-functions-unlockable-without-triggering-measured-boot
- https://github.com/lf-edge/eve
