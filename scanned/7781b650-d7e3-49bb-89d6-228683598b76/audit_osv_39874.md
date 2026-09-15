# [M] pam_usb: Unchecked integer multiplication before xmalloc() in conf.c allows heap-based buffer overflow on 32-bit targets

## Summary
Severity: Medium
Advisory: CVE-2026-48065
Aliases: GHSA-24mw-m2vf-36vp
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-48065
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.9.1, src/conf.c allocates heap memory proportional to n_devices, a count derived from libxml2 XPath evaluation of the config file, without first enforcing an upper bound. On 32-bit targets (armv7l, i686 -- both listed in the project Makefile), the multiplication n_devices * sizeof(t_pusb_device) wraps around size_t, causing xmalloc() to receive a very small size. Because xmalloc() only calls abort() on NULL return, a small-but-non-NULL allocation is accepted, and subsequent array writes overflow the heap. This vulnerability is fixed in 0.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48065.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-24mw-m2vf-36vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-48065
- https://github.com/mcdope/pam_usb/issues/352
- https://github.com/mcdope/pam_usb/issues/55
