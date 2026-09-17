# [H] pam_usb: Shell injection via device UUID and username in pamusb-conf and pamusb-agent

## Summary
Severity: High
Advisory: CVE-2026-44712
Aliases: GHSA-jgv5-w6rm-7wxg
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44712
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.8.7, a crafted UUID such as $(id>/tmp/rce) in the config causes root RCE when pamusb-conf --reset-pads is run. A USB device with a crafted filesystem UUID (some controllers allow this) can inject the payload at --add-device time. Also, userName from the XML config is passed to os.system() in pamusb-agent, which invokes a shell. This vulnerability is fixed in 0.8.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44712.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-jgv5-w6rm-7wxg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44712
