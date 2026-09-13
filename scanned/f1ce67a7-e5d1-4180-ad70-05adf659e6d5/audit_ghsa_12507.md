# [H] mockjs vulnerable to Prototype Pollution via the Util.extend function

## Summary
Severity: High
Advisory: GHSA-mh8j-9jvh-gjf6
CVE: CVE-2023-26158
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-mh8j-9jvh-gjf6
Type: github-advisory

## Affected
- npm: `mockjs` — affected >=0

## Details
All versions of the package mockjs are vulnerable to Prototype Pollution via the Util.extend function due to missing check if the attribute resolves to the object prototype. By adding or modifying attributes of an object prototype, it is possible to create attributes that exist on every object, or replace critical attributes with malicious ones. This can be problematic if the software depends on existence or non-existence of certain attributes, or uses pre-defined attributes of object prototype (such as hasOwnProperty, toString or valueOf).

User controlled inputs inside the extend() method of the Mock.Handler, Mock.Random, Mock.RE.Handler or Mock.Util, will allow an attacker to exploit this vulnerability.

 Workaround

By using a denylist of dangerous attributes, this weakness can be eliminated.

Add the following line in the Util.extend function:

js
js if (["__proto__", "constructor", "prototype"].includes(name)) continue


js
// src/mock/handler.js
Util.extend = function extend() {
        var target = arguments[0] || {},
            i = 1,
            length = arguments.length,
            options, name, src, copy, clone

        if (length === 1) {
            target = this
            i = 0
        }

        for (; i < length; i++) {
            options = arguments[i]
            if (!options) continue

            for (name in options) {
            if (["__proto__", "constructor", "prototype"].includes(name)) continue
                src = target[name]
                copy = options[name]

                if (target === copy) continue
                if (copy === undefined) continue

                if (Util.isArray(copy) || Util.isObject(copy)) {
                    if (Util.isArray(copy)) clone = src && Util.isArray(src) ? src : []
                    if (Util.isObject(copy)) clone = src && Util.isObject(src) ? src : {}

                    target[name] = Util.extend(clone, copy)
                } else {
                    target[name] = copy
                }
            }
        }

        return target
    }

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26158
- https://github.com/nuysoft/Mock
- https://github.com/nuysoft/Mock/blob/00ce04b92eb464e664a4438430903f2de96efb47/dist/mock.js#L721-L755
- https://security.snyk.io/vuln/SNYK-JS-MOCKJS-6051365
