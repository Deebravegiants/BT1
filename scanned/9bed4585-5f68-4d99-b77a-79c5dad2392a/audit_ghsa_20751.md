# [H] Incorrect Access Control and Cross Site Scripting in Jellyfin

## Summary
Severity: High
Advisory: GHSA-qwp3-5fw3-5wgv
CVE: CVE-2022-35909
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-20
Source: https://github.com/advisories/GHSA-qwp3-5fw3-5wgv
Type: github-advisory

## Affected
- NuGet: `Jellyfin.Common` — affected >=0 <10.8.0

## Details
In Jellyfin before 10.8, the /users endpoint has incorrect access control for admin functionality. This lack of access control can be leveraged to performe a cross site scripting attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35909
- https://github.com/jellyfin/jellyfin/pull/7569/files
- https://docs.google.com/document/d/1cBXQrokCvWxKET4BKi3ZLtVp5gst6-MrGPgMKpfXw8Y/edit
- https://github.com/jellyfin/jellyfin
- https://medium.com/stolabs/cve-2022-35909-cve-2022-35910-incorrect-access-control-and-xss-stored-to-jellyfin-967359c91058
