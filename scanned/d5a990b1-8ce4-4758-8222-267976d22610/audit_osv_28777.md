# [M] CVE-2024-36472

## Summary
Severity: Medium
Advisory: CVE-2024-36472
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2024-36472
Type: osv

## Details
In GNOME Shell through 45.7, a portal helper can be launched automatically (without user confirmation) based on network responses provided by an adversary (e.g., an adversary who controls the local Wi-Fi network), and subsequently loads untrusted JavaScript code, which may lead to resource consumption or other impacts depending on the JavaScript code's behavior.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36472.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36472
- https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/7688
