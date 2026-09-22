# [H] CVE-2019-20925

## Summary
Severity: High
Advisory: CVE-2019-20925
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/CVE-2019-20925
Type: osv

## Details
An unauthenticated client can trigger denial of service by issuing specially crafted wire protocol messages, which cause the message decompressor to incorrectly allocate memory. This issue affects MongoDB Server v4.2 versions prior to 4.2.1; MongoDB Server v4.0 versions prior to 4.0.13; MongoDB Server v3.6 versions prior to 3.6.15 and MongoDB Server v3.4 versions prior to 3.4.24.

## References
- https://jira.mongodb.org/browse/SERVER-43751
