# [M] isomorphic-git < 1.42.0 Prototype Pollution via getRemoteInfo

## Summary
Severity: Medium
Advisory: CVE-2026-89011
Aliases: GHSA-83vg-jxvh-fx76
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-89011
Type: osv

## Details
isomorphic-git before 1.42.0 contains a prototype pollution vulnerability in the getRemoteInfo function that allows a malicious Git server operator to pollute Object.prototype by advertising crafted ref names containing '__proto__' path segments during ref negotiation. Attackers controlling a Git server can advertise a specially crafted ref such as '__proto__/corsProxy' to reroute all subsequent network operations through an attacker-controlled proxy, causing isomorphic-git to invoke the victim's onAuth callback and transmit credentials to the attacker when the victim calls getRemoteInfo with an attacker-supplied URL.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89011.json
- https://github.com/isomorphic-git/isomorphic-git/releases/tag/v1.42.0
- https://github.com/isomorphic-git/isomorphic-git/security/advisories/GHSA-83vg-jxvh-fx76
- https://nvd.nist.gov/vuln/detail/CVE-2026-89011
- https://www.vulncheck.com/advisories/isomorphic-git-prototype-pollution-via-getremoteinfo
- https://github.com/isomorphic-git/isomorphic-git/pull/2426
- https://github.com/isomorphic-git/isomorphic-git/commit/b3db111885230bac9a648e0a2312c65ca66f76eb
- https://github.com/isomorphic-git/isomorphic-git
