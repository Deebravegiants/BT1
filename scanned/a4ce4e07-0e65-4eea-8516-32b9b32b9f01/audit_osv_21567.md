# [H] CVE-2021-44108

## Summary
Severity: High
Advisory: CVE-2021-44108
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2021-44108
Type: osv

## Details
A null pointer dereference in src/amf/namf-handler.c in Open5GS 2.3.6 and earlier allows remote attackers to Denial of Service via a crafted sbi request to amf.

## References
- https://github.com/open5gs/open5gs/issues/1247
- https://github.com/open5gs/open5gs/commit/d919b2744cd05abae043490f0a3dd1946c1ccb8c
