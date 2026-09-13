# [M] CVE-2024-38394

## Summary
Severity: Medium
Advisory: CVE-2024-38394
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-06-15
Source: https://osv.dev/vulnerability/CVE-2024-38394
Type: osv

## Details
Mismatches in interpreting USB authorization policy between GNOME Settings Daemon (GSD) through 46.0 and the Linux kernel's underlying device matching logic allow a physically proximate attacker to access some unintended Linux kernel USB functionality, such as USB device-specific kernel modules and filesystem implementations. NOTE: the GSD supplier indicates that consideration of a mitigation for this within GSD would be in the context of "a new feature, not a CVE."

## References
- https://gitlab.gnome.org/GNOME/gnome-settings-daemon/-/tags
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38394.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38394
- https://pulsesecurity.co.nz/advisories/usbguard-bypass
- https://gitlab.gnome.org/GNOME/gnome-settings-daemon/-/issues/780
- https://gitlab.gnome.org/GNOME/gnome-settings-daemon/-/issues/780#note_2047914
