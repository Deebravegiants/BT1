# [H] Gnome-remote-desktop: inadequate validation of session agents using d-bus methods may expose rdp tls certificate

## Summary
Severity: High
Advisory: CVE-2024-5148
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-02
Source: https://osv.dev/vulnerability/CVE-2024-5148
Type: osv

## Details
A flaw was found in the gnome-remote-desktop package. The gnome-remote-desktop system daemon performs inadequate validation of session agents using D-Bus methods related to transitioning a client connection from the login screen to the user session. As a result, the system RDP TLS certificate and key can be exposed to unauthorized users. This flaw allows a malicious user on the system to take control of the RDP client connection during the login screen-to-user session transition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2024-5148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5148.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5148
- https://bugzilla.redhat.com/show_bug.cgi?id=2282003
- https://gitlab.gnome.org/GNOME/gnome-remote-desktop/-/issues/196
- https://github.com/GNOME/gnome-remote-desktop
