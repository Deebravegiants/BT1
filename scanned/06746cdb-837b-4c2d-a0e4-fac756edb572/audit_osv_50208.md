# [H] CVE-2019-9503

## Summary
Severity: High
Advisory: CVE-2019-9503
CVSS: 8.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-01-16
Source: https://osv.dev/vulnerability/CVE-2019-9503
Type: osv

## Details
The Broadcom brcmfmac WiFi driver prior to commit a4176ec356c73a46c07c181c6d04039fafa34a9f is vulnerable to a frame validation bypass. If the brcmfmac driver receives a firmware event frame from a remote source, the is_wlc_event_frame function will cause this frame to be discarded and unprocessed. If the driver receives the firmware event frame from the host, the appropriate handler is called. This frame validation can be bypassed if the bus used is USB (for instance by a wifi dongle). This can allow firmware event frames from a remote source to be processed. In the worst case scenario, by sending specially-crafted WiFi packets, a remote, unauthenticated attacker may be able to execute arbitrary code on a vulnerable system. More typically, this vulnerability will result in denial-of-service conditions.

## References
- https://blog.quarkslab.com/reverse-engineering-broadcom-wireless-chipsets.html
- https://kb.cert.org/vuls/id/166939/
- https://people.canonical.com/~ubuntu-security/cve/2019/CVE-2019-9503.html
- https://security-tracker.debian.org/tracker/CVE-2019-9503
- https://bugzilla.redhat.com/show_bug.cgi?id=1701842
- https://bugzilla.suse.com/show_bug.cgi?id=1132828
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a4176ec356c73a46c07c181c6d04039fafa34a9f
