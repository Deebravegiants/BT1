# [M] CVE-2021-37938

## Summary
Severity: Medium
Advisory: CVE-2021-37938
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-11-18
Source: https://osv.dev/vulnerability/CVE-2021-37938
Type: osv

## Details
It was discovered that on Windows operating systems specifically, Kibana was not validating a user supplied path, which would load .pbf files. Because of this, a malicious user could arbitrarily traverse the Kibana host to load internal files ending in the .pbf extension. Thanks to Dominic Couture for finding this vulnerability.

## References
- https://discuss.elastic.co/t/kibana-7-15-2-security-update/288923
