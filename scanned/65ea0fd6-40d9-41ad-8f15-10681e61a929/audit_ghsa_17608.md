# [C] Teleport allows remote authentication bypass

## Summary
Severity: Critical
Advisory: GHSA-8cqv-pj7f-pwpc
CVE: CVE-2025-49825
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-8cqv-pj7f-pwpc
Type: github-advisory

## Affected
- Go: `github.com/gravitational/teleport` — affected >=17.0.0 <17.5.2
- Go: `github.com/gravitational/teleport` — affected >=16.0.0 <16.5.12
- Go: `github.com/gravitational/teleport` — affected >=15.0.0 <15.5.3
- Go: `github.com/gravitational/teleport` — affected >=14.0.0 <14.4.1
- Go: `github.com/gravitational/teleport` — affected >=13.0.0 <13.4.27
- Go: `github.com/gravitational/teleport` — affected >=0.0.11 <12.4.35
- Go: `github.com/gravitational/teleport` — affected >=0

## Details
### Impact

A full technical disclosure and open-source patch will be published after the embargo period, ending on June 30th, to allow all users to upgrade.

Teleport security engineers identified a critical security vulnerability that could allow remote authentication bypass of Teleport.  

Teleport Cloud Infrastructure and CI/CD build, test, and release infrastructure aren’t affected. 

For the full mitigation, upgrade both Proxy and Teleport agents. It is strongly recommend updating clients to the released patch versions as a precaution.


Have questions? 

- OSS Community: [opensource@goteleport.com](mailto:opensource@goteleport.com) 
- Legal: [legal@goteleport.com](mailto:legal@goteleport.com)
- Security: [security@goteleport.com](mailto:security@goteleport.com)
- Customer Support: [goteleport.com/support](https://goteleport.com/support)
- Media Inquiries: [teleport@babelpr.com](mailto:teleport@babelpr.com)

### Patches

Fixed in versions: 17.5.2, 16.5.12, 15.5.3, 14.4.1, 13.4.27, 12.4.35.

These patches are available only on the [official Teleport distribution channels](https://goteleport.com/docs/installation/). 

These versions are designated as _Critical Security Exception Versions_. 

_For these specific patch versions of Teleport Community Edition, the Community Edition restrictions are removed on employee count or revenue thresholds, as long as you apply the patch within thirty (30) days of its official release._

_Please read the full text of the updated Teleport Community Edition license for details._

## References
- https://github.com/gravitational/teleport/security/advisories/GHSA-8cqv-pj7f-pwpc
- https://nvd.nist.gov/vuln/detail/CVE-2025-49825
- https://github.com/gravitational/teleport
