# [M] CVE-2026-41253

## Summary
Severity: Medium
Advisory: CVE-2026-41253
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-41253
Type: osv

## Details
In iTerm2 through 3.6.9, displaying a .txt file can cause code execution via DCS 2000p and OSC 135 data, if the working directory contains a malicious file whose name is valid output from the conductor encoding path, such as a pathname with an initial ace/c+ substring, aka "hypothetical in-band signaling abuse." This occurs because iTerm2 accepts the SSH conductor protocol from terminal output that does not originate from a legitimate conductor session.

## References
- https://iterm2.com/downloads.html
- https://news.ycombinator.com/item?id=47809190
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41253.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41253
- https://github.com/gnachman/iTerm2/commit/a9e745993c2e2cbb30b884a16617cd5495899f86
- https://blog.calif.io/p/mad-bugs-even-cat-readmetxt-is-not
