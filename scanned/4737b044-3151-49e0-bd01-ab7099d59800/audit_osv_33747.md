# [H] CVE-2025-49809

## Summary
Severity: High
Advisory: CVE-2025-49809
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-49809
Type: osv

## Details
mtr through 0.95, in certain privileged contexts, mishandles execution of a program specified by the MTR_PACKET environment variable. NOTE: mtr on macOS may often have Sudo rules, as an indirect consequence of Homebrew not installing setuid binaries.

## References
- https://github.com/traviscross/mtr/blob/master/SECURITY
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49809.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49809
- https://github.com/Homebrew/homebrew-core/issues/35085
- https://github.com/traviscross/mtr/commit/5226f105f087c29d3cfad9f28000e7536af91ac6
