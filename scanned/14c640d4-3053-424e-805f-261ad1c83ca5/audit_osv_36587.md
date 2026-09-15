# [C] Unsafe variable evaluation in email templates

## Summary
Severity: Critical
Advisory: CVE-2026-2451
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P/RE:L/U:Red)
Published: 2026-02-16
Source: https://osv.dev/vulnerability/CVE-2026-2451
Type: osv

## Details
Emails sent by pretix can utilize placeholders that will be filled with customer data. For example, when {name}
 is used in an email template, it will  be replaced with the buyer's 
name for the final email. This mechanism contained a security-relevant bug:

It was possible to exfiltrate information about the pretix system through specially crafted placeholder names such as {{event.__init__.__code__.co_filename}}.
 This way, an attacker with the ability to control email templates 
(usually every user of the pretix backend) could retrieve sensitive 
information from the system configuration, including even database 
passwords or API keys. pretix does include mechanisms to prevent the usage of such 
malicious placeholders, however due to a mistake in the code, they were 
not fully effective for this plugin.

Out of caution, we recommend that you rotate all passwords and API keys contained in your pretix.cfg file.

## References
- https://marketplace.pretix.eu/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2451.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2451
- https://pretix.eu/about/en/blog/20260216-release-2026-1-1/
