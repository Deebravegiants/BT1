# [H] CVE-2019-11279

## Summary
Severity: High
Advisory: CVE-2019-11279
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/CVE-2019-11279
Type: osv

## Details
CF UAA versions prior to 74.1.0 can request scopes for a client that shouldn't be allowed by submitting an array of requested scopes. A remote malicious user can escalate their own privileges to any scope, allowing them to take control of UAA and the resources it controls.

## References
- https://www.cloudfoundry.org/blog/cve-2019-11279
