# [M] CVE-2021-21323

## Summary
Severity: Medium
Advisory: CVE-2021-21323
Aliases: GHSA-mqjf-9x5g-2rv6
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-21323
Type: osv

## Details
Brave is an open source web browser with a focus on privacy and security. In Brave versions 1.17.73-1.20.103, the CNAME adblocking feature added in Brave 1.17.73 accidentally initiated DNS requests that bypassed the Brave Tor proxy. Users with adblocking enabled would leak DNS requests from Tor windows to their DNS provider. (DNS requests that were not initiated by CNAME adblocking would go through Tor as expected.) This is fixed in Brave version 1.20.108

## References
- https://github.com/brave/brave-browser/security/advisories/GHSA-mqjf-9x5g-2rv6
- https://hackerone.com/reports/1077022
- https://github.com/brave/brave-browser/issues/13527
- https://github.com/brave/brave-core/commit/12fe321eaad8acc1cbd1d70b4128f687777bcf15
- https://github.com/brave/brave-core/pull/7769
