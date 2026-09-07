# [H] Cross-Site Scripting in Wagtail

## Summary
Severity: High
Advisory: GHSA-2473-9hgq-j7xw
CVE: CVE-2020-15118
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-07-20
Source: https://github.com/advisories/GHSA-2473-9hgq-j7xw
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=2.8rc1 <2.9.3
- PyPI: `wagtail` — affected >=0 <2.7.4

## Details
### Impact
When a form page type is made available to Wagtail editors through the `wagtail.contrib.forms` app, and the page template is built using Django's standard form rendering helpers such as `form.as_p` ([as directed in the documentation](https://docs.wagtail.io/en/stable/reference/contrib/forms/index.html#usage)), any HTML tags used within a form field's help text will be rendered unescaped in the page. Allowing HTML within help text is [an intentional design decision](https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.Field.help_text) by Django; however, as a matter of policy Wagtail does not allow editors to insert arbitrary HTML by default, as this could potentially be used to carry out cross-site scripting attacks, including privilege escalation. This functionality should therefore not have been made available to editor-level users.

The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches
Patched versions have been released as Wagtail 2.7.4 (for the LTS 2.7 branch) and Wagtail 2.9.3 (for the current 2.9 branch). In these versions, help text will be escaped to prevent the inclusion of HTML tags. Site owners who wish to re-enable the use of HTML within help text (and are willing to accept the risk of this being exploited by editors) may set `WAGTAILFORMS_HELP_TEXT_ALLOW_HTML = True` in their configuration settings.

### Workarounds
Site owners who are unable to upgrade to the new versions can secure their form page templates by [rendering forms field-by-field as per Django's documentation](https://docs.djangoproject.com/en/3.0/topics/forms/#looping-over-the-form-s-fields), but omitting the `|safe` filter when outputting the help text.

### Acknowledgements
Many thanks to Timothy Bautista for reporting this issue.

### For more information
If you have any questions or comments about this advisory:
* Visit Wagtail's [support channels](https://docs.wagtail.io/en/stable/support.html)
* Email us at [security@wagtail.io](mailto:security@wagtail.io) (if you wish to send encrypted email, the public key ID is `0x6ba1e1a86e0f8ce8`)

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-2473-9hgq-j7xw
- https://nvd.nist.gov/vuln/detail/CVE-2020-15118
- https://github.com/wagtail/wagtail/commit/d9a41e7f24d08c024acc9a3094940199df94db34
- https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.Field.help_text
- https://docs.wagtail.io/en/stable/reference/contrib/forms/index.html#usage
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2020-154.yaml
- https://github.com/wagtail/wagtail
- https://github.com/wagtail/wagtail/blob/master/docs/releases/2.9.3.rst
