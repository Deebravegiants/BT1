# [C] CVE-2021-41093

## Summary
Severity: Critical
Advisory: CVE-2021-41093
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/CVE-2021-41093
Type: osv

## Details
Wire is an open source secure messenger. In affected versions if the an attacker gets an old but valid access token they can take over an account by changing the email. This issue has been resolved in version 3.86 which uses a new endpoint which additionally requires an authentication cookie. See wire-ios-sync-engine and wire-ios-transport references. This is the root advisory that pulls the changes together.

## References
- https://github.com/wireapp/wire-ios-sync-engine/security/advisories/GHSA-w727-5f74-49xj
- https://github.com/wireapp/wire-ios-transport/security/advisories/GHSA-p354-6r3m-g4xr
- https://github.com/wireapp/wire-ios/security/advisories/GHSA-6f4c-phfj-m255
- https://github.com/wireapp/wire-server/security/advisories/GHSA-9rm2-w6pq-333m
- https://github.com/wireapp/wire-ios/commit/b0e7bb3b13dd8212032cb46e32edf701694687c7
