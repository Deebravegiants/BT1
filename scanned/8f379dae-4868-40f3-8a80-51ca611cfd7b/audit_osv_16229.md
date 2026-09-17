# [M] CVE-2019-3788

## Summary
Severity: Medium
Advisory: CVE-2019-3788
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-04-25
Source: https://osv.dev/vulnerability/CVE-2019-3788
Type: osv

## Details
Cloud Foundry UAA Release, versions prior to 71.0, allows clients to be configured with an insecure redirect uri. Given a UAA client was configured with a wildcard in the redirect uri's subdomain, a remote malicious unauthenticated user can craft a phishing link to get a UAA access code from the victim.

## References
- https://www.cloudfoundry.org/blog/cve-2019-3788
