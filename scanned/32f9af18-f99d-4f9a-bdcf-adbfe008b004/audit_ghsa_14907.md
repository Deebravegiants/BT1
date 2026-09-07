# [M] Cross-site scripting (XSS) vulnerability in Description metadata

## Summary
Severity: Medium
Advisory: GHSA-5pxr-7m4j-jjc6
CVE: CVE-2024-37160
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-5pxr-7m4j-jjc6
Type: github-advisory

## Affected
- Packagist: `getformwork/formwork` — affected >=0 <1.13.1
- Packagist: `getformwork/formwork` — affected >=2.0.0-beta.1 <2.0.0-beta.2

## Details
### Summary
Regardless of the role or privileges, no user should be able to inject malicious JavaScript (JS) scripts into the body HTML. an XSS (Cross-Site Scripting) vulnerability, specifically a Stored XSS, which affects all pages of the website. Once the JS script is embedded in the body HTML, the XSS will trigger on any page a victim visits, such as the about, blog, contact, or any other pages, except for the panel.

### Impact
This vulnerability allows attackers to inject malicious JS or HTML through a crafted payload into the vulnerable spot, achieving persistence and attacking numerous visitors or anyone accessing the website. The attack can be widespread and affect many users because the malicious JS will execute on every page, unlike an injection on a specific page (e.g., injecting on the About page would only affect that page). In this case, a single injection point leads to the execution of the malicious JS on all pages.

### Patches
- [**Formwork 1.13.1**](https://github.com/getformwork/formwork/releases/tag/1.13.1) has been released with a patch that solves this vulnerability by escaping all metadata attributes.
- [**Formwork 2.x** (f531201)](https://github.com/getformwork/formwork/commit/f5312015a5a5e89b95ef2bd07e496f8474d579c5) also escapes metadata attributes.

### Details
An attackers (requires administrator privilege) to execute arbitrary web scripts by modifying site options via /panel/options/site. This type of attack is suitable for persistence, affecting visitors across all pages (except the dashboard).

## References
- https://github.com/getformwork/formwork/security/advisories/GHSA-5pxr-7m4j-jjc6
- https://nvd.nist.gov/vuln/detail/CVE-2024-37160
- https://github.com/getformwork/formwork/commit/9d471204f7ebb51c3c27131581c2b834315b5e0b
- https://github.com/getformwork/formwork/commit/f5312015a5a5e89b95ef2bd07e496f8474d579c5
- https://github.com/getformwork/formwork
