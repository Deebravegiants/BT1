# [M] Epiphany: address bar / host spoofing via userinfo in ephy_uri_get_decoded_host()

## Summary
Severity: Medium
Advisory: CVE-2026-18487
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-18487
Type: osv

## Details
A flaw was found in Epiphany. An issue in how the browser reads web addresses allows attackers to fake the domain name shown in the address bar. If a user clicks a specially crafted link containing a colon (for example, [https://trusted.com:80@attacker.com/](https://trusted.com:80@attacker.com/)), the address bar and security menus will display the safe website (trusted.com) but it will actually load the attacker website (attacker.com) on the screen. This allows attackers to create convincing phishing pages to trick users into trusting a malicious site.

## References
- https://gitlab.gnome.org/GNOME/epiphany/-/work_items/2897
- https://access.redhat.com/security/cve/CVE-2026-18487
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18487.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18487
- https://bugzilla.redhat.com/show_bug.cgi?id=2509570
- https://gitlab.gnome.org/GNOME/epiphany/-/commit/0dde1d369458ac5c44b74b5ad3c433f825f6f8af
- https://gitlab.gnome.org/GNOME/epiphany
