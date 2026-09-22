# [M] pam_usb: XPath injection via PAM-supplied identifiers in pam_usb configuration queries

## Summary
Severity: Medium
Advisory: CVE-2026-47273
Aliases: GHSA-vfj3-5h5v-6g93
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-47273
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.9.0, pam_usb builds XPath expressions from user-supplied identifiers (PAM username, service name) and device-supplied identifiers (USB device serial, model, vendor) to query /etc/pamusb.conf. These identifiers were not validated for XPath metacharacters, allowing injection of arbitrary XPath predicates. This vulnerability is fixed in 0.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47273.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-vfj3-5h5v-6g93
- https://nvd.nist.gov/vuln/detail/CVE-2026-47273
- https://github.com/mcdope/pam_usb/commit/721fed08a3596cb5b4671ad702f8fdc12dcc7420
- https://github.com/mcdope/pam_usb/pull/311
