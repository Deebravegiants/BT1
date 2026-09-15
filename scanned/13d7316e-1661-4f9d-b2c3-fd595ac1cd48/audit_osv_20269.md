# [H] CVE-2021-32663

## Summary
Severity: High
Advisory: CVE-2021-32663
Aliases: GHSA-ghqc-r8f6-q9m9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-10-19
Source: https://osv.dev/vulnerability/CVE-2021-32663
Type: osv

## Details
iTop is an open source web based IT Service Management tool. In affected versions an attacker can call the system setup without authentication. Given specific parameters this can lead to SSRF. This issue has been resolved in versions 2.6.5 and 2.7.5 and later

## References
- https://github.com/Combodo/iTop/security/advisories/GHSA-ghqc-r8f6-q9m9
- https://github.com/Combodo/iTop/commit/43daa2ef088bf928a2386fa19324628c3f19b807
- https://github.com/Combodo/iTop/commit/6be9a87c150978752bc68baae1a5c4833ddadfec
