# [M] guzzlehttp/guzzle-services' XML Request Serialization Vulnerable to XML Injection via CDATA Terminator

## Summary
Severity: Medium
Advisory: GHSA-q8r6-5hfw-5jff
CVE: CVE-2026-53723
CWE: CWE-20, CWE-91
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-q8r6-5hfw-5jff
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle-services` — affected >=0 <1.5.4

## Details
### Impact

`guzzlehttp/guzzle-services` does not safely serialize scalar XML element values containing the CDATA terminator `]]>`. The XML request serializer writes values containing `<`, `>`, or `&` with `XMLWriter::writeCData($value)`. If attacker-controlled input contains `]]>`, the CDATA section closes early and the remainder is interpreted as XML markup. This is an outgoing request-body integrity issue, not a response parsing issue. The attacker does not need to control the service description or schema.

Users are affected when all of the following are true:

1. The application uses `guzzlehttp/guzzle-services` to serialize outgoing requests.
2. A request parameter or `additionalParameters` schema uses `location: xml`.
3. The value is serialized as XML element text, not an XML attribute.
4. The value can contain attacker-controlled, user-controlled, tenant-controlled, or otherwise untrusted input.
5. The value is not constrained by a safe `enum`, `pattern`, or custom filter that excludes `]]>`.
6. The downstream service parses the generated XML structurally and may act on unexpected, duplicated, or injected elements.

Applications that serialize untrusted input into `location: xml` request parameters can emit XML containing attacker-controlled elements outside the intended text node. Depending on the receiving service, this can alter operation semantics, smuggle privileged fields, bypass modeled parameter boundaries, or create conflicting duplicated elements. Fixed service descriptions are sufficient if they contain an XML element parameter populated from attacker-controlled input.

Users are not directly affected if they only use Guzzle Services to deserialize HTTP response bodies. Response XML parsing uses the response XML location visitor and does not invoke the vulnerable request XML serializer. Response bodies matter only in a second-order flow, such as parsing attacker-controlled response XML, storing or forwarding a parsed string value, and later using it as a `location: xml` request parameter.

Example fixed service description:

```php
'DisplayName' => ['location' => 'xml', 'type' => 'string']
```

If an attacker-controlled display name is:

```text
Alice]]></DisplayName><Role>admin</Role><DisplayName><![CDATA[
```

the vulnerable serializer can emit an injected element outside the intended `DisplayName` text node:

```xml
<Request><DisplayName><![CDATA[Alice]]></DisplayName><Role>admin</Role><DisplayName><![CDATA[]]></DisplayName></Request>
```

If the downstream service treats `<Role>` as meaningful, the attacker has set a field the modeled `DisplayName` parameter was not intended to set.

### Patches

The issue is patched in `1.5.4` and later by safely splitting embedded CDATA terminators before serialization. The fix preserves the original scalar value as XML text and prevents injected nodes.

### Workarounds

If you cannot upgrade immediately, constrain attacker-controlled XML element values with a strict `enum`, `pattern`, or custom filter that excludes `]]>`, or avoid serializing untrusted data into `location: xml` element text until patched. Where appropriate for the service schema, XML attributes are not affected because they are written with XMLWriter attribute APIs rather than CDATA sections.

To determine whether action is needed, search service descriptions for request parameters using `location: xml`, including operation `parameters` and `additionalParameters`. Response-only `models` are not directly affected unless parsed values are reused for request serialization. For object and array parameters, review nested scalar properties because leaf element values can still be affected.

### References

- https://www.w3.org/TR/xml/#sec-cdata-sect
- https://www.php.net/manual/en/xmlwriter.writecdata.php
- https://www.php.net/manual/en/xmlwriter.text.php

## References
- https://github.com/guzzle/guzzle-services/security/advisories/GHSA-q8r6-5hfw-5jff
- https://nvd.nist.gov/vuln/detail/CVE-2026-53723
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/guzzle-services/CVE-2026-53723.yaml
- https://github.com/guzzle/guzzle-services
