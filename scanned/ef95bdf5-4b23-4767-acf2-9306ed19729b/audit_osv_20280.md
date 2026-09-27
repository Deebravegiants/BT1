# [M] CVE-2021-32698

## Summary
Severity: Medium
Advisory: CVE-2021-32698
Aliases: GHSA-mh6g-62p8-26m4
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-21
Source: https://osv.dev/vulnerability/CVE-2021-32698
Type: osv

## Details
eLabFTW is an open source electronic lab notebook for research labs. This vulnerability allows an attacker to make GET requests on behalf of the server. It is "blind" because the attacker cannot see the result of the request. Issue has been patched in eLabFTW 4.0.0.

## References
- https://github.com/elabftw/elabftw/commit/3d2db4d3ad90b0915f29f05aeba41eaaf6a7c726
- https://github.com/elabftw/elabftw/security/advisories/GHSA-mh6g-62p8-26m4
