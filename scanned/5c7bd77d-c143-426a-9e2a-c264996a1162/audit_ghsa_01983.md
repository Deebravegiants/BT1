# [H] Exposure of Sensitive Information to an Unauthorized Actor in foreman_fog_proxmox

## Summary
Severity: High
Advisory: GHSA-f2rp-4rv7-fc95
CVE: CVE-2021-20259
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-10
Source: https://github.com/advisories/GHSA-f2rp-4rv7-fc95
Type: github-advisory

## Affected
- RubyGems: `foreman_fog_proxmox` — affected >=0 <0.13.1

## Details
A flaw was found in the Foreman project. The Proxmox compute resource exposes the password through the API to an authenticated local attacker with view_hosts permission. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability. Versions of foreman_fog_proxmox prior to 0.13.1 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20259
- https://github.com/theforeman/foreman_fog_proxmox/pull/184/commits/b7e910bf61563f5d447c71b1b41e2a373a794d7b
- https://bugzilla.redhat.com/show_bug.cgi?id=1932144
- https://github.com/theforeman/foreman_fog_proxmox
- https://github.com/theforeman/foreman_fog_proxmox/releases/tag/v0.13.1
