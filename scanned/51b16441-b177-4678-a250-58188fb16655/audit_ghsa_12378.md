# [C] Pedroetb TTS-API OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-jx6q-fq9h-6g7q
CVE: CVE-2019-25158
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-19
Source: https://github.com/advisories/GHSA-jx6q-fq9h-6g7q
Type: github-advisory

## Affected
- npm: `tts-api` — affected >=0 <2.2.0

## Details
A vulnerability has been found in pedroetb tts-api up to 2.1.4 and classified as critical. This vulnerability affects the function onSpeechDone of the file app.js. The manipulation leads to os command injection. Upgrading to version 2.2.0 is able to address this issue. The patch is identified as 29d9c25415911ea2f8b6de247cb5c4607d13d434. It is recommended to upgrade the affected component. VDB-248278 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25158
- https://github.com/pedroetb/tts-api/commit/29d9c25415911ea2f8b6de247cb5c4607d13d434
- https://github.com/pedroetb/tts-api
- https://github.com/pedroetb/tts-api/releases/tag/v2.2.0
- https://vuldb.com/?ctiid.248278
- https://vuldb.com/?id.248278
