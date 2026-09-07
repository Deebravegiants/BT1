# [M] LeafKit's HTML escaping may be skipped for Collection values, enabling XSS

## Summary
Severity: Medium
Advisory: GHSA-6jj5-j4j8-8473
CVE: CVE-2026-28499
CWE: CWE-116, CWE-79, CWE-80
Ecosystem: SwiftURL
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-6jj5-j4j8-8473
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/leaf-kit` — affected >=0 <1.14.2

## Details
### Summary
LeafKit HTML-escaping is not working correctly when a template prints a collection (Array / Dictionary) via `#(value)`. This can result in XSS, allowing potentially untrusted input to be rendered unescaped.

### Details
LeafKit attempts to escape expressions during serialization, but due to [`LeafData.htmlEscaped()`](https://github.com/vapor/leaf-kit/blob/8ff06839d8b3ddf74032d2ade01e3453eb556d30/Sources/LeafKit/LeafData/LeafData.swift#L322)'s implementation, when the escaped type's conversion to `String` is marked as `.ambiguous` (as it is the case for Arrays and Dictionaries), an unescaped `self` is returned.

> **Note: I recommend first looking at the POC, before taking a look at the details below, as it is simple.** In the detailed, verbose analysis below, I explored the functions involved in more detail, in hopes that it will help you understand and locate this issue.

#### The issue's detailed analysis:
1. Leaf expression serialization eventually reaches `LeafSerializer`'s `serialize` private function below.  This is where the `leafData` is `.htmlEscaped()`, and then serialized.

https://github.com/vapor/leaf-kit/blob/8ff06839d8b3ddf74032d2ade01e3453eb556d30/Sources/LeafKit/LeafSerialize/LeafSerializer.swift#L60-L66

2. The `LeafData.htmlEscaped()` method uses the `LeafData.string` computed property to convert itself to a string. Then, it calls the `htmlEscaped()` method on it. However, if the string conversion fails, notice that an unescaped, unsafe `self` is returned (line 324 below):

https://github.com/vapor/leaf-kit/blob/8ff06839d8b3ddf74032d2ade01e3453eb556d30/Sources/LeafKit/LeafData/LeafData.swift#L321-L328


3. Regarding why `.string` may return nil, if the escaped value is not a string already, a convesion is attempted, which may fail.

https://github.com/vapor/leaf-kit/blob/8ff06839d8b3ddf74032d2ade01e3453eb556d30/Sources/LeafKit/LeafData/LeafData.swift#L211-L216

In this specific case, the conversion fails at line 303 below, when `conversion.is >= level` is checked. The check fails because [`.array` and `.dictionary` conversions to `.string` are deemed `.ambiguous`](https://github.com/vapor/leaf-kit/blob/8ff06839d8b3ddf74032d2ade01e3453eb556d30/Sources/LeafKit/LeafData/LeafData.swift#L525-L535). If we forcefully allow ambiguous conversions, the vulnerability disappears, as the conversion is successful.

https://github.com/vapor/leaf-kit/blob/8ff06839d8b3ddf74032d2ade01e3453eb556d30/Sources/LeafKit/LeafData/LeafData.swift#L295-L319

5. Coming back to `LeafSerializer`'s `serialize` private method, we are now interested in finding out what happens after `LeafData.htmlEscaped()` returns self. Recall from `1.` that the output was then `.serialized()`. Thus, the unescaped `LeafData` follows the normal serialization path, as if it were HTML-escaped. More specifically, serialization is done [here](https://github.com/vapor/leaf-kit/blob/8ff06839d8b3ddf74032d2ade01e3453eb556d30/Sources/LeafKit/LeafData/LeafDataStorage.swift#L52-L63), where `.map` / `.mapValues` is called, unsafely serializing each element of the dictionary.

### PoC
<!-- _Complete instructions, including specific configuration details, to reproduce the vulnerability._ -->

In a new Vapor project created with `vapor new poc -n --leaf`, use a simple leaf template like the following:
```html
<!doctype html>
<html>
    <body>
    <h1>#(username)</h1>
      <h2>someDict:</h2>
      <p>#(someDict)</p>
  </body>
</html>
```

And the following `routes.swift`:
```swift
import Vapor

struct User: Encodable {
    var username: String
    var someDict: [String: String]
}

func routes(_ app: Application) throws {
    app.get { req async throws in
        try await req.view.render("index", User(
            username: "Escaped XSS - <img src=x onerror=alert(1)>",
            someDict: ["<img src=x onerror=alert(1337)>":"<img src=x onerror=alert(31337)>"]
        ))
    }
}

```

By running and accessing the server in a browser, XSS should be triggered twice (with `alert(1337)` and `alert(31337)`). `var someDict: [String: String]` could also be replaced with an array / dictionary of a different type, such as another `Encodable` stuct.

Also note that, in a real concerning scenario, the array / dictionary would contain (i.e. reflect) data inputted by the user.

### Impact
This is a cross-site scripting (XSS) vulnerability in rendered Leaf templates. Vapor/Leaf applications that render user-controlled data inside arrays or dictionaries using `#(value)` may be impacted.

## References
- https://github.com/vapor/leaf-kit/security/advisories/GHSA-6jj5-j4j8-8473
- https://nvd.nist.gov/vuln/detail/CVE-2026-28499
- https://github.com/vapor/leaf-kit/commit/6044b844caa858a0c5f2505ac166f5a057c990dc
- https://github.com/vapor/leaf-kit
- https://github.com/vapor/leaf-kit/releases/tag/1.14.2
