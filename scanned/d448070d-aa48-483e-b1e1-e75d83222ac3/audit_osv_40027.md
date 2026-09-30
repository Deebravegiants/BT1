# [M] pam_usb: xmlReadFile flags=0 permits XXE network entity fetching in conf.c

## Summary
Severity: Medium
Advisory: CVE-2026-48981
Aliases: GHSA-96vv-r4wc-28c2
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:L/A:L)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-48981
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. In versions prior to 0.9.2, pam_usb calls xmlReadFile() with flags=0 when loading the configuration file, allowing libxml2 to process external entity references (XXE), potentially making outbound network connections or local file reads at XML parse time from the context of the authenticating process. The vulnerability requires the configuration file to contain crafted XML entity references. Since pam_usb.conf is root-owned, direct exploitation requires prior write access to the config, but the defence-in-depth impact is significant given that pam_usb.so runs in setuid contexts (sudo, su). This issue has been fixed in version 0.9.2.

## References
- https://github.com/mcdope/pam_usb/releases/tag/0.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48981.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-96vv-r4wc-28c2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48981
