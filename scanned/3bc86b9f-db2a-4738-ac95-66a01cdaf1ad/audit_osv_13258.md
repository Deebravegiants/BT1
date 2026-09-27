# [C] CVE-2018-18925

## Summary
Severity: Critical
Advisory: CVE-2018-18925
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-04
Source: https://osv.dev/vulnerability/CVE-2018-18925
Type: osv

## Details
Gogs 0.11.66 allows remote code execution because it does not properly validate session IDs, as demonstrated by a ".." session-file forgery in the file session provider in file.go. This is related to session ID handling in the go-macaron/session code for Macaron.

## References
- https://github.com/gogs/gogs/issues/5469
