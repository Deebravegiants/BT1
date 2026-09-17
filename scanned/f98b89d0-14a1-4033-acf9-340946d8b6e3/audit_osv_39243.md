# [H] pam_usb: PINENTRY_FALLBACK_APP environment variable allows arbitrary command execution

## Summary
Severity: High
Advisory: CVE-2026-44709
Aliases: GHSA-jxrj-q67x-wr4c
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44709
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.8.7, pamusb-pinentry reads the PINENTRY_FALLBACK_APP environment variable and executes it directly without any validation. Any process that can set environment variables before pamusb-pinentry is invoked can point PINENTRY_FALLBACK_APP at an arbitrary binary or script and have it executed with the privileges of the pam_usb tool chain. This vulnerability is fixed in 0.8.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44709.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-jxrj-q67x-wr4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-44709
