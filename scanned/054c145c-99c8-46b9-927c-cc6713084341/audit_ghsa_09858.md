# [M] Home Assistant Command-line Interface: Handling of user-supplied Jinja2 templates

## Summary
Severity: Medium
Advisory: GHSA-33qf-q99x-wpm8
CVE: CVE-2026-40602
CWE: CWE-1336, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-33qf-q99x-wpm8
Type: github-advisory

## Affected
- PyPI: `homeassistant-cli` — affected >=0 <1.0.0

## Details
### Impact

Up to 1.0.0 of `home-assitant-cli` (or `hass-cli` for short) an unrestricted environment was used to handle Jninja2 templates instead of a sandboxed one. The user-supplied input within Jinja2 templates was rendered locally with no restrictions. This gave users access to Python's internals and extended the scope of templating beyond the intended usage.

E. g., it was possible to render a template with `hass-cli template bad-template.j2 --local` that contained entries like

````j2
{%- set b   = environ.__globals__['__builtins__'] -%}
{%- set os  = b['__import__']('os') -%}
{%- set bio = b['__import__']('builtins') -%}
...
````

or other malicious Jinja2 expressions. This can lead to arbitrary code execution on the local machine.

In a two step process an adversary could trick/convince an user to download third-party templates which contain harmful code (e. g., perform data manipulation or establish a remote shell)  then to render those templates unchecked/reviewed/verified with `--local`. 

The issue only affect the local machine and not a remote Home Assistant instance. It also requires user interventions.

### Patches

1.0.0 uses `ImmutableSandboxedEnvironment` and restricts the usage of environment variables.

### Workarounds

Evaluate the Jninja2 templates manually or  tool-based before rendering with `hass-cli`.

## References
- https://github.com/home-assistant-ecosystem/home-assistant-cli/security/advisories/GHSA-33qf-q99x-wpm8
- https://nvd.nist.gov/vuln/detail/CVE-2026-40602
- https://github.com/home-assistant-ecosystem/home-assistant-cli/pull/453
- https://github.com/home-assistant-ecosystem/home-assistant-cli
