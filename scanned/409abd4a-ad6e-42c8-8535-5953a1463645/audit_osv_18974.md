# [M] CVE-2020-5401

## Summary
Severity: Medium
Advisory: CVE-2020-5401
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2020-5401
Type: osv

## Details
Cloud Foundry Routing Release, versions prior to 0.197.0, contains GoRouter, which allows malicious clients to send invalid headers, causing caching layers to reject subsequent legitimate clients trying to access the app.

## References
- https://www.cloudfoundry.org/blog/cve-2020-5401
