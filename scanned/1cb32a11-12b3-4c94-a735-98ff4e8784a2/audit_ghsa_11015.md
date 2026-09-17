# [H] dynaconf Affected by Remote Code Execution (RCE) via Insecure Template Evaluation in @jinja Resolver

## Summary
Severity: High
Advisory: GHSA-pxrr-hq57-q35p
CVE: CVE-2026-33154
CWE: CWE-1336, CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-pxrr-hq57-q35p
Type: github-advisory

## Affected
- PyPI: `dynaconf` — affected >=0 <3.2.13

## Details
### Summary
Dynaconf is vulnerable to Server-Side Template Injection (SSTI) due to unsafe template evaluation in the @jinja resolver.
When the jinja2 package is installed, Dynaconf evaluates template expressions embedded in configuration values without a sandboxed environment.

If an attacker can influence configuration sources such as:
environment variables
.env files
container environment configuration
CI/CD secrets
they can execute arbitrary OS commands on the host system.
In addition, the @format resolver allows object graph traversal, which may expose sensitive runtime objects and environment variables.

### Details
The vulnerability arises because Dynaconf's string resolvers lack proper security boundaries.

1. @jinja Resolver
The @jinja resolver renders templates using full Jinja2 evaluation.
However, the rendering context is not sandboxed, which allows attackers to access Python's internal attributes.
Using objects such as cycler, attackers can reach Python's __globals__ and import the os module.

Example attack path
cycler
 → __init__
 → __globals__
 → os
 → popen()
This leads to arbitrary command execution.

2. @format Resolver
The @format resolver performs Python string formatting using internal objects.
This allows attackers to traverse Python's object graph and access sensitive runtime objects.
Example traversal:
{this.__class__.__init__.__globals__[os].environ}
This can expose
- API keys
- database credentials
- internal service tokens
- environment secrets

### PoC
```
import os
from dynaconf import Dynaconf
# Malicious configuration injection
os.environ["DYNACONF_RCE"] = "@jinja {{ cycler.__init__.__globals__.os.popen('id').read() }}"
settings = Dynaconf()
print("[!] Command Execution Result:")
print(settings.RCE)
```
### Impact
Successful exploitation allows attackers to:
- Execute arbitrary OS commands on the host system
- Access sensitive environment variables
- Compromise application secrets
- Fully compromise the running application process
Because configuration values may originate from CI/CD pipelines, container orchestration systems, or environment injection, this vulnerability can become remotely exploitable in real-world deployments.


### Remediation / Mitigation (Examples)

1. Use Jinja2 sandbox for template rendering
```
from jinja2.sandbox import SandboxedEnvironment
env = SandboxedEnvironment()
template = env.from_string("{{ config_value }}")
safe_value = template.render(config_value=user_input)```
```
2. Restrict @format usage to trusted values
```
safe_value = "{name}".format(name=trusted_name)
```

## References
- https://github.com/dynaconf/dynaconf/security/advisories/GHSA-pxrr-hq57-q35p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33154
- https://github.com/dynaconf/dynaconf/commit/2fbb45ee36b8c0caa5b924fe19f3c1a5e8603fa7
- https://github.com/dynaconf/dynaconf
- https://github.com/dynaconf/dynaconf/releases/tag/3.2.13
