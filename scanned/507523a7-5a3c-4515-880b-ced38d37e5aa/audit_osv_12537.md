# [M] CVE-2018-1268

## Summary
Severity: Medium
Advisory: CVE-2018-1268
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-06-06
Source: https://osv.dev/vulnerability/CVE-2018-1268
Type: osv

## Details
Cloud Foundry Loggregator, versions 89.x prior to 89.5 or 96.x prior to 96.1 or 99.x prior to 99.1 or 101.x prior to 101.9 or 102.x prior to 102.2, does not validate app GUID structure in requests. A remote authenticated malicious user knowing the GUID of an app may construct malicious requests to read from or write to the logs of that app.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1268
