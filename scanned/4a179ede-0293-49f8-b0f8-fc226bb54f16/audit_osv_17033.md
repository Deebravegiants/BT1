# [C] CVE-2020-11535

## Summary
Severity: Critical
Advisory: CVE-2020-11535
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2020-11535
Type: osv

## Details
An issue was discovered in ONLYOFFICE Document Server 5.5.0. An attacker can craft a malicious .docx file, and exploit XML injection to enter an attacker-controlled parameter into the x2t binary, to rewrite this binary and/or libxcb.so.1, and execute code on a victim's server.

## References
- https://gist.github.com/andrewaeva/beb92d3d2f1c5672dbda5050e323f6a0
- https://github.com/ONLYOFFICE/DocumentServer/blob/master/CHANGELOG.md#551
