# [M] Partial Server-Side Request Forgery in Home Assistant Core

## Summary
Severity: Medium
Advisory: CVE-2023-41899
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-19
Source: https://osv.dev/vulnerability/CVE-2023-41899
Type: osv

## Details
Home assistant is an open source home automation. In affected versions the `hassio.addon_stdin` is vulnerable to a partial Server-Side Request Forgery where an attacker capable of calling this service (e.g.: through GHSA-h2jp-7grc-9xpp) may be able to invoke any Supervisor REST API endpoints with a POST request. An attacker able to exploit will be able to control the data dictionary, including its addon and input key/values. This issue has been addressed in version 2023.9.0 and all users are advised to upgrade. There are no known workarounds for this vulnerability. This issue is also tracked as GitHub Security Lab (GHSL) Vulnerability Report: `GHSL-2023-162`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41899.json
- https://github.com/home-assistant/core/security/advisories/GHSA-4r74-h49q-rr3h
- https://github.com/home-assistant/core/security/advisories/GHSA-h2jp-7grc-9xpp
- https://nvd.nist.gov/vuln/detail/CVE-2023-41899
