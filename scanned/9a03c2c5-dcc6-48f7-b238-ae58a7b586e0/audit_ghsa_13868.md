# [H] Nautobot vulnerable to remote code execution via Jinja2 template rendering

## Summary
Severity: High
Advisory: GHSA-8mfq-f5wj-vw5m
CVE: CVE-2023-25657
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-22
Source: https://github.com/advisories/GHSA-8mfq-f5wj-vw5m
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=0 <1.5.7

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

All users of Nautobot versions earlier than 1.5.7 are impacted.

In Nautobot 1.5.7 we have enabled sandboxed environments for the Jinja2 template engine used internally for template rendering for the following objects:

- `extras.ComputedField`
- `extras.CustomLink`
- `extras.ExportTemplate` 
- `extras.Secret`
- `extras.Webhook`

While we are not aware of any active exploits, we have made this change as a preventative measure to protect against any potential remote code execution attacks utilizing maliciously crafted template code.

This change forces the Jinja2 template engine to use a [`SandboxedEnvironment`](https://jinja.palletsprojects.com/en/3.0.x/sandbox/#sandbox) on all new installations of Nautobot.

This addresses any potential unsafe code execution everywhere the helper function `nautobot.utilities.utils.render_jinja2` is called. Additionally, our documentation that was previously suggesting the direct use of `jinja2.Template` has been revised to utilize `render_jinja2`.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Yes. Users should upgrade to Nautobot 1.5.7 or newer.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

##### Enabling Sandboxed Environments

For users that are unable to upgrade to the latest release of Nautobot, you may add the following setting to your `nautobot_config.py` to apply the sandbox environment enforcement:

```python
TEMPLATES[1]["OPTIONS"]["environment"] = "jinja2.sandbox.SandboxedEnvironment"
```

After applying this change, you must restart all Nautobot services, including any Celery worker processes.

**Note:** *Nautobot specifies two template engines by default, the first being “django” for the Django built-in template engine, and the second being “jinja” for the Jinja2 template engine. This recommended setting will update the second item in the list of template engines, which is the Jinja2 engine.*

##### Restricting Jinja2 using Access Controls

For users that are unable to immediately update their configuration such as if a Nautobot service restart is too disruptive to operations, access to provide custom Jinja2 template values may be mitigated using permissions to restrict “change” (write) actions to the affected object types listed in the first section.

**Note:** *This solution is intended to be stopgap until you can successfully update your `nautobot_config.py` or upgrade your Nautobot instance to apply the sandboxed environment enforcement.*

#### Updating Existing App or Job Code

For Nautobot App (formerly plugin) authors or Job authors, additionally we recommend that if you have any custom code that may for example be using `jinaj2.Template` that you no longer use that. Instead, please always use our `nautobot.utilities.utils.render_jinja2` function which will make sure that the centrally-provided Jinja2 template engine with sandboxing enforced is being utilized.

Anywhere you’ve been using this pattern:

```python
from jinja2 import Template

my_template = Template(template_code)
config = my_template.render(context)
```

We recommend that you replace it with this pattern:

```python
from nautobot.utilities.utils import render_jinja2
    
config = render_jinja2(template_code, context)
```

### References
_Are there any links users can visit to find out more?_

Please see the Nautobot 1.5.7 release notes. 

https://docs.nautobot.com/projects/core/en/stable/release-notes/version-1.5/#v157-2023-01-04

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-8mfq-f5wj-vw5m
- https://nvd.nist.gov/vuln/detail/CVE-2023-25657
- https://github.com/nautobot/nautobot/commit/d47f157e83b0c353bb2b697f911882c71cf90ca0
- https://docs.nautobot.com/projects/core/en/stable/release-notes/version-1.5/#v157-2023-01-04
- https://github.com/nautobot/nautobot
- https://github.com/pypa/advisory-database/tree/main/vulns/nautobot/PYSEC-2023-37.yaml
- https://jinja.palletsprojects.com/en/3.0.x/sandbox/#sandbox
