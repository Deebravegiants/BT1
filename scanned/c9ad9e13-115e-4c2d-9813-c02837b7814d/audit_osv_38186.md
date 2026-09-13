# [M] Chyrp Lite has an IDOR via Mass Assignment in Post Model

## Summary
Severity: Medium
Advisory: CVE-2026-35173
Aliases: GHSA-8c3h-rh2j-fxr9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35173
Type: osv

## Details
Chyrp Lite is an ultra-lightweight blogging engine. Prior to 2026.01, an IDOR / Mass Assignment issue exists in the Post model that allows authenticated users with post editing permissions (Edit Post, Edit Draft, Edit Own Post, Edit Own Draft) to modify posts they do not own and do not have permission to edit. By passing internal class properties such as id into the post_attributes payload, an attacker can alter the object being instantiated. As a result, further actions are performed on another user’s post rather than the attacker’s own post, effectively enabling post takeover. This vulnerability is fixed in 2026.01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35173.json
- https://github.com/xenocrat/chyrp-lite/security/advisories/GHSA-8c3h-rh2j-fxr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-35173
