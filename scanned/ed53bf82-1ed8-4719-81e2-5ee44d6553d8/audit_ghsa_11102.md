# [M] django-unicorn affected by component state manipulation via unvalidated attribute access

## Summary
Severity: Medium
Advisory: GHSA-ffv6-jj46-x367
CVE: CVE-2026-31815
CWE: CWE-284, CWE-915
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-ffv6-jj46-x367
Type: github-advisory

## Affected
- PyPI: `django-unicorn` — affected >=0 <0.67.0

## Details
## Summary
Component state manipulation is possible in `django-unicorn` due to missing access control checks during property updates and method calls. An attacker can bypass the intended `_is_public` protection to modify internal attributes such as `template_name` or trigger protected methods.

## Vulnerability Details: Component Access Control Bypass
Security analysis identified that the framework fails to enforce visibility boundaries defined by `_is_public` within the action parsers. Specifically, the logic in `set_property_value()` and `_call_method_name()` utilizes `getattr` and `setattr` directly on component instances without verifying if the target attribute or method is explicitly marked as public.

Vulnerability resides in:
- `src/django_unicorn/views/action_parsers/call_method.py`
- `src/django_unicorn/views/action_parsers/utils.py`

While Django's template engine restricts rendering to registered directories, an unauthorized user can still force a component to render sensitive templates (e.g., admin layouts) from other installed applications or reset the component state by invoking the internal `reset()` method.

## Proof of Concept (PoC)
Attacker can overwrite the `template_name` attribute by sending a crafted JSON payload to the message endpoint:

1. Construct a payload targeting a protected attribute:
   ```json
   {
     "actionQueue": [
       {
         "type": "syncInput",
         "payload": { "name": "template_name", "value": "admin/base.html" }
       }
     ],
     "data": {},
     "meta": "<checksum_of_empty_dict>"
   }
   ```
2. The server-side component updates its internal state: `self.template_name = "admin/base.html"`.
3. Subsequent re-rendering displays the content of the targeted template, bypassing intended component logic.

## Impact
Low severity. The risk is limited to unauthorized manipulation of component state and rendering of existing templates within the application's configured template directories. Remote Code Execution (RCE) is not possible via this vector.

## References
- https://github.com/django-commons/django-unicorn/security/advisories/GHSA-ffv6-jj46-x367
- https://nvd.nist.gov/vuln/detail/CVE-2026-31815
- https://github.com/django-commons/django-unicorn
