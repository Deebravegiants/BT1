# [H] pam_usb: Symlink attacks on pad directory and pad files enable authentication bypass and root file corruption

## Summary
Severity: High
Advisory: CVE-2026-44711
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44711
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.8.7, symlink attacks on pad directory and pad files enable authentication bypass and root file corruption. This vulnerability is fixed in 0.8.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44711.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-fjpm-p9pj-mp34
- https://nvd.nist.gov/vuln/detail/CVE-2026-44711
- https://github.com/uniget-org/cli/security/advisories/GHSA-qqq4-5773-pmw5
