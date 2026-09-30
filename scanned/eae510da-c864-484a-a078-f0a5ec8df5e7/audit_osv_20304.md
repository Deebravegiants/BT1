# [M] CVE-2021-32750

## Summary
Severity: Medium
Advisory: CVE-2021-32750
Aliases: GHSA-68xh-9h7w-64qg
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-07-15
Source: https://osv.dev/vulnerability/CVE-2021-32750
Type: osv

## Details
MuWire is a file publishing and networking tool that protects the identity of its users by using I2P technology. Users of MuWire desktop client prior to version 0.8.8 can be de-anonymized by an attacker who knows their full ID. An attacker could send a message with a subject line containing a URL with an HTML image tag and the MuWire client would try to fetch that image via clearnet, thus exposing the IP address of the user. The problem is fixed in MuWire 0.8.8. As a workaround, users can disable messaging functionality to prevent other users from sending them malicious messages.

## References
- https://github.com/zlatinb/muwire/security/advisories/GHSA-68xh-9h7w-64qg
