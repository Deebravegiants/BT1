# [M] Zeep: Server-Side Request Forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-4cc2-g9w2-fhf6
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-4cc2-g9w2-fhf6
Type: github-advisory

## Affected
- PyPI: `zeep` — affected >=4.0.0 <4.3.3

## Details
## Summary

When parsing a WSDL or XSD document, python-zeep follows transitive references — xsd:import, xsd:include, wsdl:import, and lxml entity/DTD resolution — and will fetch http/https URLs found in those references. The Settings.forbid_external option, intended to disable this transitive remote fetching, was defined but not wired to any logic from version 4.0.0 through 4.3.2 (a regression introduced when zeep moved off defusedxml in 4.0). As a result, setting `forbid_external=True` had no effect, and applications that processed untrusted or attacker-influenced WSDL/XSD documents could be coerced into making server-side requests to arbitrary URLs (SSRF).

## Impact

Server-Side Request Forgery (SSRF), CWE-918.

An attacker who can supply or influence the contents of a WSDL/XSD that an application loads with zeep can embed an import/include reference (e.g. `<xsd:import schemaLocation="http://169.254.169.254/...">`) pointing at an internal or otherwise sensitive endpoint. When zeep parses the document it transitively fetches that URL using the configured transport, causing the application to issue outbound requests to attacker-chosen destinations. This can be used to reach internal-only services, cloud metadata endpoints, or other hosts not directly reachable by the attacker, and may disclose response timing/behaviour.

Impacted users are those who:

- load WSDL/XSD documents that are untrusted or whose import targets an attacker can control, and/or
- relied on `forbid_external=True` as a security control — in 4.0.0–4.3.2 that setting silently did nothing, so the protection users believed they had was not in effect.

Note the default was (and remains) `forbid_external=False`, i.e. transitive remote fetching is permitted by default; the security defect is specifically that the opt-out control was non-functional.

## Patches

Fixed in python-zeep 4.3.3. The forbid_external setting is now enforced: when set to True, zeep refuses to transitively fetch http/https resources via `xsd:import`, `xsd:include`, `wsdl:import`, or lxml entity/DTD resolution, raising `zeep.exceptions.ExternalReferenceForbidden`. The user-supplied entry-point WSDL/schema URL is still loaded.

Affected versions: >= 4.0.0, < 4.3.3.

Upgrade to 4.3.3 (or later) and set forbid_external=True when loading documents from untrusted sources:

```python
from zeep import Client, Settings

settings = Settings(forbid_external=True)
client = Client("https://untrusted.example/service?wsdl", settings=settings)
```

## Workarounds

If you cannot upgrade to 4.3.3:

- Do not load untrusted WSDL/XSD documents, and avoid loading WSDLs whose import/include targets can be influenced by untrusted input.
- Vendor the schema locally: pre-fetch and review the WSDL and all of its imported schemas, then load them from local files (e.g. file:// paths) so no remote fetching occurs at parse
  time.
- Restrict egress at the network layer: block outbound traffic from the host/process to internal ranges and metadata endpoints (e.g. 169.254.169.254, RFC1918 ranges) so SSRF attempts
  cannot reach sensitive targets.
- Use a restrictive custom Transport: subclass the zeep transport and reject/allow-list URLs in load() so disallowed hosts are never fetched.

## References
- https://github.com/mvantellingen/python-zeep/security/advisories/GHSA-4cc2-g9w2-fhf6
- https://github.com/mvantellingen/python-zeep/commit/83eb07bc6c84d841329d4f88856fecdba86f753e
- https://github.com/mvantellingen/python-zeep
- https://github.com/mvantellingen/python-zeep/releases/tag/4.3.3
