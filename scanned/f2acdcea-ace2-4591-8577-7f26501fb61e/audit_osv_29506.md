# [H] JavaScript specification issue may lead to type confusion and pointer dereference in implementations

## Summary
Severity: High
Advisory: CVE-2024-43357
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-08-15
Source: https://osv.dev/vulnerability/CVE-2024-43357
Type: osv

## Details
ECMA-262 is the language specification for the scripting language ECMAScript. A problem in the ECMAScript (JavaScript) specification of async generators, introduced by a May 2021 spec refactor, may lead to mis-implementation in a way that could present as a security vulnerability, such as type confusion and pointer dereference.

The internal async generator machinery calls regular promise resolver functions on IteratorResult (`{ done, value }`) objects that it creates, assuming that the IteratorResult objects will not be then-ables. Unfortunately, these IteratorResult objects inherit from `Object.prototype`, so these IteratorResult objects can be made then-able, triggering arbitrary behaviour, including re-entering the async generator machinery in a way that violates some internal invariants.

The ECMAScript specification is a living standard and the issue has been addressed at the time of this advisory's public disclosure. JavaScript engine implementors should refer to the latest specification and update their implementations to comply with the `AsyncGenerator` section.

## References

- https://github.com/tc39/ecma262/commit/1e24a286d0a327d08e1154926b3ee79820232727
- https://bugzilla.mozilla.org/show_bug.cgi?id=1901411
- https://github.com/boa-dev/boa/security/advisories/GHSA-f67q-wr6w-23jq
- https://bugs.webkit.org/show_bug.cgi?id=275407
- https://issues.chromium.org/issues/346692561
- https://www.cve.org/CVERecord?id=CVE-2024-7652

## References
- https://bugs.webkit.org/show_bug.cgi?id=275407
- https://issues.chromium.org/issues/346692561
- https://tc39.es/ecma262/#sec-asyncgenerator-objects
- https://www.cve.org/CVERecord?id=CVE-2024-7652
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43357.json
- https://github.com/boa-dev/boa/security/advisories/GHSA-f67q-wr6w-23jq
- https://github.com/tc39/ecma262/security/advisories/GHSA-g38c-wh3c-5h9r
- https://nvd.nist.gov/vuln/detail/CVE-2024-43357
- https://bugzilla.mozilla.org/show_bug.cgi?id=1901411
- https://github.com/tc39/ecma262/commit/1e24a286d0a327d08e1154926b3ee79820232727
- https://github.com/tc39/ecma262/commit/4cb5a6980e20be76c648f113c4cc762342172df3
- https://github.com/tc39/ecma262/pull/2413
