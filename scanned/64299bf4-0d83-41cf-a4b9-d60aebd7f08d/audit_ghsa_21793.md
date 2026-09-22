# [H] Infinite loop in Yubico yubihsm-connector

## Summary
Severity: High
Advisory: GHSA-8m9g-647g-5pxw
CVE: CVE-2021-28484
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N/E:U/RL:O/RC:R (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-8m9g-647g-5pxw
Type: github-advisory

## Affected
- Go: `github.com/Yubico/yubihsm-connector` — affected >=0 <3.0.1

## Details
An issue was discovered in the /api/connector endpoint handler in Yubico yubihsm-connector before 3.0.1 (in YubiHSM SDK before 2021.04). The handler did not validate the length of the request, which can lead to a state where yubihsm-connector becomes stuck in a loop waiting for the YubiHSM to send it data, preventing any further operations until the yubihsm-connector is restarted. An attacker can send 0, 1, or 2 bytes to trigger this.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28484
- https://github.com/Yubico/yubihsm-connector/commit/82bdf202c53460bac9106cc9b4b34a0a16cae0ed
- https://github.com/Yubico/yubihsm-connector/releases
- https://www.yubico.com/support/security-advisories/ysa-2021-02
