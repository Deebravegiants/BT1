# [H] fast-xml-builder allows attribute values with unwanted quotes to bypass malicious or unwanted attributes

## Summary
Severity: High
Advisory: GHSA-5wm8-gmm8-39j9
CVE: CVE-2026-44665
CWE: CWE-611, CWE-91
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-5wm8-gmm8-39j9
Type: github-advisory

## Affected
- npm: `fast-xml-builder` — affected >=0 <1.1.7

## Details
# Summary
When an input data has quotes in attribute values but process entities is not enabled, it breaks the attribute value into multiple attributes. This gives the room for an attacker to insert unwanted attributes to the XML/HTML.

## Detail

Malicious Input
```
{
      a: {
        "@_attr": '" onClick="alert(1)'
      }
}
```

Output
```xml
<a attr="" onClick="alert(1)"></a>
```

### Workarounds
If you're not ignoring attributes then keep processEntities flag true.

## References
- https://github.com/NaturalIntelligence/fast-xml-builder/security/advisories/GHSA-5wm8-gmm8-39j9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44665
- https://github.com/NaturalIntelligence/fast-xml-builder
