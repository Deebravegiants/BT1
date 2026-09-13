# [H] pretix unsafely evaluates variables in emails

## Summary
Severity: High
Advisory: GHSA-r8p8-qw9w-j9qv
CVE: CVE-2026-2415
CWE: CWE-627
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-16
Source: https://github.com/advisories/GHSA-r8p8-qw9w-j9qv
Type: github-advisory

## Affected
- PyPI: `pretix` — affected >=2026.1.0 <2026.1.1
- PyPI: `pretix` — affected >=2025.10.0 <2025.10.2
- PyPI: `pretix` — affected >=0 <2025.9.4

## Details
Emails sent by pretix can utilize placeholders that will be filled with customer data. For example, when `{name}` is used in an email template, it will  be replaced with the buyer's name for the final email. This mechanism contained two security-relevant bugs:

 -  It was possible to exfiltrate information about the pretix system through specially crafted placeholder names such as `{event.__init__.__code__.co_filename}}`. This way, an attacker with the ability to control email templates (usually every user of the pretix backend) could retrieve sensitive information from the system configuration, including even database passwords or API keys. pretix does include mechanisms to prevent the usage of such malicious placeholders, however due to a mistake in the code, they were not fully effective for the email subject.

 -  Placeholders in subjects and plain text bodies of emails were wrongfully evaluated twice. Therefore, if the first evaluation of a placeholder again contains a placeholder, this second placeholder was rendered. This allows the rendering of placeholders controlled by the ticket buyer, and therefore the exploitation of the first issue as a ticket buyer. Luckily, the only buyer-controlled placeholder available in pretix by default (that is not validated in a way that prevents the issue) is `{invoice_company}`, which is very unusual (but not impossible) to be contained in an email subject template. In addition to broadening the attack surface of the first issue, this could theoretically also leak information about an order to one of the attendees within that order. However, we also consider this scenario very unlikely under typical conditions.

Out of caution, pretix recommend that you rotate all passwords and API keys contained in your pretix.cfg https://docs.pretix.eu/self-hosting/config/  file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2415
- https://github.com/pretix/pretix/commit/ba11d24f8dfa4e9d8f03493e56fd8b43983fe297
- https://github.com/pretix/pretix/commit/c85afbc621b5f0b1afa618627c45f89323eb0154
- https://github.com/pretix/pretix/commit/edac35ed4c5466eb63a202575c337d117ddf1c8e
- https://github.com/pretix/pretix
- https://pretix.eu/about/en/blog/20260216-release-2026-1-1
