# [M] protobufjs: Text Format string map parsing can mutate returned map object prototype

## Summary
Severity: Medium
Advisory: GHSA-jfj6-75fj-8934
CVE: CVE-2026-59876
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-jfj6-75fj-8934
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=8.2.0 <8.6.5

## Details
## Summary

The protobuf.js text format extension parsed string-keyed map entries using ordinary property assignment. A text-format map entry with key `__proto__` could therefore change the prototype of the returned map object instead of creating an own map entry.

This affected the optional Text Format extension. Other protobufjs input paths, including binary decode, `fromObject`, and ProtoJSON conversion, are not affected.

## Impact

An attacker who can provide protobuf text-format input parsed by an application using `protobufjs/ext/textformat` may be able to create message objects whose string-keyed map fields have attacker-controlled prototypes.

This is per-object prototype mutation, not global `Object.prototype` pollution. Impact depends on downstream application logic treating inherited properties as meaningful, for example by using `in`, truthiness checks, or direct property access on parsed map objects instead of own-property checks.

Applications that do not parse untrusted Text Format input, or that do not use inherited properties from parsed map objects in security-relevant logic, are not directly affected.

## Preconditions

* The application must parse attacker-controlled protobuf Text Format input with `protobufjs/ext/textformat`.
* The target schema must contain a string-keyed map field.
* The crafted input must provide a map entry with key `__proto__`.
* Downstream application logic must treat inherited properties on the returned map object as meaningful for impact beyond malformed output.

## Workarounds

Upgrade to protobufjs 8.6.5 or newer.

If immediate upgrade is not possible, do not parse untrusted protobuf Text Format input with affected versions. Applications can also reject string map keys named `__proto__` before or during Text Format parsing, and should use own-property checks such as `Object.hasOwnProperty.call(map, key)` when consuming parsed map objects.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-jfj6-75fj-8934
- https://nvd.nist.gov/vuln/detail/CVE-2026-59876
- https://github.com/protobufjs/protobuf.js/pull/2335
- https://github.com/protobufjs/protobuf.js/commit/9f97fe413072d3beb52c74e62d88ea8adc9444d8
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.6.5
