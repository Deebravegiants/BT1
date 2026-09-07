# [M] October CMS Vulnerable to Stored XSS via Editor and Branding Styles

## Summary
Severity: Medium
Advisory: GHSA-gxxc-m74c-f48x
CVE: CVE-2025-61674
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-gxxc-m74c-f48x
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=0 <3.7.13
- Packagist: `october/system` — affected >=4.0.0 <4.0.12

## Details
A cross-site scripting (XSS) vulnerabilities was identified in October CMS backend configuration forms:

- **Editor Settings Markup Styles**  
   A user with the `Global Editor Settings` permission could inject malicious HTML/JS into the stylesheet input at  
   *Settings → Editor Settings → Markup Styles*.  

A specially crafted input could break out of the intended `<style>` context, allowing arbitrary script execution across backend pages for all users.

---

### Impact
- Persistent XSS across the backend interface.  
- Exploitable by lower-privileged accounts with the above permissions.  
- Potential consequences include privilege escalation, session hijacking, and execution of unauthorized actions in victim sessions.

---

### Patches
The vulnerability has been patched in **v4.0.12** and **v3.7.13**.  
Stylesheet inputs are now sanitized to prevent injection of arbitrary HTML/JS.  

All users are strongly encouraged to upgrade to the latest patched version.

---

### Workarounds
If upgrading immediately is not possible:  
- Restrict the permissions `Global Editor Settings` to fully trusted administrators only.  

This reduces exposure but does not fully eliminate risk.

---

### Credits
- Reported by **[Nakkouch Tarek](https://github.com/nakkouchtarek)**

## References
- https://github.com/octobercms/october/security/advisories/GHSA-gxxc-m74c-f48x
- https://nvd.nist.gov/vuln/detail/CVE-2025-61674
- https://github.com/octobercms/october
