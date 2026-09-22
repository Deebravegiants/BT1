# [H] OctoPrint has possible file exfiltration via query parameters on upload endpoints

## Summary
Severity: High
Advisory: GHSA-j4h9-pm27-4rfw
CVE: CVE-2026-54134
CWE: CWE-436, CWE-73
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-j4h9-pm27-4rfw
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.11.8
- PyPI: `OctoPrint` — affected >=2.0.0rc1 <2.0.0rc3

## Details
### Impact

OctoPrint versions up until and including 1.11.7 as well as 2.0.0rc1 and 2.0.0rc2 contain a vulnerability that allows an attacker with the `FILE_UPLOAD` permission to exfiltrate files from the host that OctoPrint has read access to, by moving them into the upload folder where they then can be downloaded from. This vulnerability was already reported as [GHSA-m9jh-jf9h-x3h2/CVE-2025-48067](https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-m9jh-jf9h-x3h2) but the fix provided in OctoPrint 1.11.2 turned out to be incomplete.

The primary risk lies in the potential exfiltration of secrets stored inside OctoPrint's config, or further system files. By removing important runtime files, this could also be used to impact the availability of the host after an attempted server restart. Given that the attacker requires a user account with file upload permissions, the actual impact of this should however hopefully be minimal in most cases.

### Patches

The vulnerability has been patched in version 1.11.8 and 2.0.0rc3.

### Details

OctoPrint's web application is implemented in Flask, but uploads are first intercepted by a custom upload handler built on Tornado that sits in front of it. The handler streams the upload to a temporary file on disk - so files larger than the available memory can be uploaded - and rewrites the request, adding internal form fields that tell Flask where to find that temporary file.

These fields are reserved and meant to be set only by the upload handler, never by the client. The previous fix from [GHSA-m9jh-jf9h-x3h2/CVE-2025-48067](https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-m9jh-jf9h-x3h2) stripped them from the request received from the client when they were sent as multipart form fields, yet they could still reach Flask through other channels: as plain query parameters, or - since the Tornado handler and Flask did not parse requests identically - smuggled in via several "parser differentials" that looked harmless to the handler while Flask still saw the injected fields. Any of these let an attacker make OctoPrint treat an arbitrary file on the host as a freshly uploaded one and move it into the upload folder.

The following endpoints in OctoPrint are affected:

- `/api/files/{local|sdcard}`
- `/api/languages`
- `/plugin/backup/restore`
- `/plugin/pluginmanager/upload_file`

Further upload endpoints in third party plugins might be affected too.

The fix rejects requests carrying any of the reserved fields, aligns the Tornado handler's request parsing with Flask's (Werkzeug) to avoid any differential parsing, and re-validates the request rewritten by Tornado before forwarding it to Flask.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Koh Jun Sheng and Jacopo Tediosi.

### Timeline

2026-06-04: Report received
2026-06-04: Report acknowledged
2026-06-08: Report verified
2026-06-17: Fix ready for 1.11.x
2026-06-22: Fix ported to 2.0.0
2026-06-23: Fix released with 1.11.8 and 2.0.0rc3

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-j4h9-pm27-4rfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-54134
- https://github.com/OctoPrint/OctoPrint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2026-2687.yaml
