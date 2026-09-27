# [M] ezsystems/ez-support-tools Failing access control in system info view

## Summary
Severity: Medium
Advisory: GHSA-xmp3-7745-g4vj
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-xmp3-7745-g4vj
Type: github-advisory

## Affected
- Packagist: `ezsystems/ez-support-tools` — affected >=2.2.0 <2.2.3

## Details
This Security Advisory is about a vulnerability in ezsystems/ez-support-tools v2.2, part of Ibexa DXP v3.2. Older versions are not affected. A user having insufficient permissions is able to access the system information tabs if they type in the direct link (the link is not shown in the menu). The "Setup / System info" policy should be required to access it, but only backend login is actually required. This means any editor can see core system information, including the output from phpinfo(). The fix ensures that the access policy is correctly verified.

## References
- https://developers.ibexa.co/security-advisories/ibexa-sa-2020-007-failing-access-control-in-system-info-view
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ez-support-tools/2020-12-01-1.yaml
- https://github.com/ezsystems/ez-support-tools
