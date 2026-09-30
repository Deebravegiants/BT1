# [H] Networkmanager-libreswan: local privilege escalation via leftupdown

## Summary
Severity: High
Advisory: CVE-2024-9050
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-22
Source: https://osv.dev/vulnerability/CVE-2024-9050
Type: osv

## Details
A flaw was found in the libreswan client plugin for NetworkManager (NetkworkManager-libreswan), where it fails to properly sanitize the VPN configuration from the local unprivileged user. In this configuration, composed by a key-value format, the plugin fails to escape special characters, leading the application to interpret values as keys. One of the most critical parameters that could be abused by a malicious user is the `leftupdown`key. This key takes an executable command as a value and is used to specify what executes as a callback in NetworkManager-libreswan to retrieve configuration settings back to NetworkManager. As NetworkManager uses Polkit to allow an unprivileged user to control the system's network configuration, a malicious actor could achieve local privilege escalation and potential code execution as root in the targeted machine by creating a malicious configuration.

## References
- http://www.openwall.com/lists/oss-security/2024/10/25/1
- https://access.redhat.com/downloads/content/package-browser/
- https://www.openwall.com/lists/oss-security/2024/10/25/1
- https://access.redhat.com/errata/RHSA-2024:8312
- https://access.redhat.com/errata/RHSA-2024:8338
- https://access.redhat.com/errata/RHSA-2024:8352
- https://access.redhat.com/errata/RHSA-2024:8353
- https://access.redhat.com/errata/RHSA-2024:8354
- https://access.redhat.com/errata/RHSA-2024:8355
- https://access.redhat.com/errata/RHSA-2024:8356
- https://access.redhat.com/errata/RHSA-2024:8357
- https://access.redhat.com/errata/RHSA-2024:8358
- https://access.redhat.com/errata/RHSA-2024:9555
- https://access.redhat.com/errata/RHSA-2024:9556
- https://access.redhat.com/security/cve/CVE-2024-9050
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9050.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9050
- https://bugzilla.redhat.com/show_bug.cgi?id=2313828
- https://gitlab.gnome.org/GNOME/NetworkManager-libreswan/-/commit/dcf8acfb25bd31e4b8cbd20c229da660238b5c1b
- https://gitlab.gnome.org/GNOME/NetworkManager-libreswan/
