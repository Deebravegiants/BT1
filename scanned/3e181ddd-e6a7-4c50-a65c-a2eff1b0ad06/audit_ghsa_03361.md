# [H] Improper validation of URLs ('Cross-site Scripting') in Wagtail rich text fields

## Summary
Severity: High
Advisory: GHSA-wq5h-f9p5-q7fx
CVE: CVE-2021-29434
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-wq5h-f9p5-q7fx
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <2.11.7
- PyPI: `wagtail` — affected >=2.12 <2.12.4

## Details
### Impact
When saving the contents of a rich text field in the admin interface, Wagtail does not apply server-side checks to ensure that link URLs use a valid protocol. A malicious user with access to the admin interface could thus craft a POST request to publish content with `javascript:` URLs containing arbitrary code. The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches
Patched versions have been released as Wagtail 2.11.7 (for the LTS 2.11 branch) and Wagtail 2.12.4 (for the current 2.12 branch).

### Workarounds
For sites that cannot easily upgrade to a current supported version, the vulnerability can be patched by adding the following code to a `wagtail_hooks.py` module in any installed app:

```python
from draftjs_exporter.dom import DOM
from wagtail.admin.rich_text.converters.html_to_contentstate import ExternalLinkElementHandler, PageLinkElementHandler
from wagtail.core import hooks
from wagtail.core.whitelist import check_url


def link_entity(props):
    id_ = props.get('id')
    link_props = {}

    if id_ is not None:
        link_props['linktype'] = 'page'
        link_props['id'] = id_
    else:
        link_props['href'] = check_url(props.get('url'))

    return DOM.create_element('a', link_props, props['children'])


@hooks.register('register_rich_text_features', order=1)
def register_link(features):
    features.register_converter_rule('contentstate', 'link', {
        'from_database_format': {
            'a[href]': ExternalLinkElementHandler('LINK'),
            'a[linktype="page"]': PageLinkElementHandler('LINK'),
        },
        'to_database_format': {
            'entity_decorators': {'LINK': link_entity}
        }
    })
```

### Acknowledgements
Many thanks to Kevin Breen for reporting this issue.

### For more information
If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.io/en/stable/support.html)
* Email us at security@wagtail.io (if you wish to send encrypted email, the public key ID is `0x6ba1e1a86e0f8ce8`)

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-wq5h-f9p5-q7fx
- https://nvd.nist.gov/vuln/detail/CVE-2021-29434
- https://github.com/wagtail/wagtail/commit/5c7a60977cba478f6a35390ba98cffc2bd41c8a4
- https://github.com/wagtail/wagtail/commit/915f6ed2bd7d53154103cc4424a0f18695cdad6c
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2021-114.yaml
- https://github.com/wagtail/wagtail
- https://github.com/wagtail/wagtail/compare/v2.11.6...v2.11.7
- https://pypi.org/project/wagtail
