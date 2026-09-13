# [M] CVE-2021-22151

## Summary
Severity: Medium
Advisory: CVE-2021-22151
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-11-22
Source: https://osv.dev/vulnerability/CVE-2021-22151
Type: osv

## Details
It was discovered that Kibana was not validating a user supplied path, which would load .pbf files. Because of this, a malicious user could arbitrarily traverse the Kibana host to load internal files ending in the .pbf extension.

## References
- https://discuss.elastic.co/t/elastic-stack-7-14-1-security-update/283077
- https://www.elastic.co/community/security
