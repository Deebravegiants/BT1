# [M] CVE-2019-3990

## Summary
Severity: Medium
Advisory: CVE-2019-3990
Aliases: GHSA-6qj9-33j4-rvhg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-3990
Type: osv

## Details
A User Enumeration flaw exists in Harbor. The issue is present in the "/users" API endpoint. This endpoint is supposed to be restricted to administrators. This restriction is able to be bypassed and information can be obtained about registered users can be obtained via the "search" functionality.

## References
- https://www.tenable.com/security/research/tra-2019-50
- https://github.com/goharbor/harbor/security/advisories/GHSA-6qj9-33j4-rvhg
