# [H] Nim's rst parser sandboxed mode allows include which can embed any local file

## Summary
Severity: High
Advisory: CVE-2022-23602
Aliases: GHSA-q3vh-x957-wr75
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-02-01
Source: https://osv.dev/vulnerability/CVE-2022-23602
Type: osv

## Details
Nimforum is a lightweight alternative to Discourse written in Nim. In versions prior to 2.2.0 any forum user can create a new thread/post with an include referencing a file local to the host operating system. Nimforum will render the file if able. This can also be done silently by using NimForum's post "preview" endpoint. Even if NimForum is running as a non-critical user, the forum.json secrets can be stolen. Version 2.2.0 of NimForum includes patches for this vulnerability. Users are advised to upgrade as soon as is possible. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23602.json
- https://github.com/nim-lang/nimforum/security/advisories/GHSA-q3vh-x957-wr75
- https://nvd.nist.gov/vuln/detail/CVE-2022-23602
- https://github.com/nim-lang/Nim/commit/cb894c7094fb49014f85815a9dafc38b5dda743e
