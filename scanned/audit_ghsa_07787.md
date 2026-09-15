# [H] AVideo has Authenticated Server-Side Request Forgery via downloadURL in aVideoEncoder.json.php

## Summary
Severity: High
Advisory: GHSA-h39h-7cvg-q7j6
CVE: CVE-2026-27732
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-h39h-7cvg-q7j6
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <22.0

## Details
### Vulnerability Type
Authenticated Server-Side Request Forgery (SSRF)

### Affected Product/Versions
AVideo versions prior to 22 (tested on AVideo 21.x).

### Root Cause Summary
The `aVideoEncoder.json.php` API endpoint accepts a `downloadURL` parameter and fetches the referenced resource server-side without proper validation or an allow-list. This allows authenticated users to trigger server-side requests to arbitrary URLs (including internal network endpoints).

### Impact Summary
An authenticated attacker can leverage SSRF to interact with internal services and retrieve sensitive data (e.g., internal APIs, metadata services), potentially leading to further compromise depending on the deployment environment.

### Resolution/Fix
This issue has been fixed in AVideo version 22. Users should upgrade to version 22.0 as soon as possible.

### Credits/Acknowledgement
Thanks to Arkadiusz Marta for responsibly reporting this issue.
- GitHub Profile: https://github.com/arkmarta/

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-h39h-7cvg-q7j6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27732
- https://github.com/WWBN/AVideo/commit/384ef2548093f4cbb1bfac00f1f429fe57fab853
- https://github.com/WWBN/AVideo
- https://github.com/WWBN/AVideo/releases/tag/22.0
