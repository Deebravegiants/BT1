# [H] ALPINE-CVE-2023-46136

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-46136
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46136
Type: osv

## Affected
- Alpine:v3.23: `py3-werkzeug` — affected >=0 <2.3.7-r0
- Alpine:v3.24: `py3-werkzeug` — affected >=0 <2.3.7-r0

## Details
Werkzeug is a comprehensive WSGI web application library. In versions on the 3.x branch prior to 3.0.1 and on the 2.x branch prior to 2.3.8, if an upload of a file that starts with CR or LF and then is followed by megabytes of data without these characters: all of these bytes are appended chunk by chunk into internal bytearray and lookup for boundary is performed on growing buffer. This allows an attacker to cause a denial of service by sending crafted multipart data to an endpoint that will parse it. The amount of CPU time required can block worker processes from handling legitimate requests. This vulnerability has been patched in version 3.0.1 and 2.3.8.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46136
