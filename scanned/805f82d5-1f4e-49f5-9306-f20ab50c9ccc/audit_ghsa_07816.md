# [M] Leaf-kit html escaping does not work on characters that are part of extended grapheme cluster

## Summary
Severity: Medium
Advisory: GHSA-4hfh-fch3-5q7p
CVE: CVE-2026-27120
CWE: CWE-75, CWE-79, CWE-87
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-4hfh-fch3-5q7p
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/leaf-kit` — affected >=0 <1.4.1

## Details
### Summary

`htmlEscaped` in leaf-kit will only escape html  special characters if the extended grapheme clusters match, which allows bypassing escaping by using an extended grapheme cluster containing both the special html character and some additional characters. In the case of html attributes, this can lead to XSS if there is a leaf variable in the attribute that is user controlled.

### Details

Relevant code:
https://github.com/vapor/leaf-kit/blob/main/Sources/LeafKit/String%2BHTMLEscape.swift#L14

Strings in Swift are based on extended grapheme clusters. HTML on the other hand is based on unicode characters. 

For example if you have the sequence "́  (U+0022 Quotation mark followed by U+0301 Combining Acute Accent). To HTML this is just a quote mark followed by some other random character. To swift this is one extended grapheme cluster that does not equal a quotation mark by itself which is a different extended grapheme cluster.

Thus `"\"́".replacingOccurrences(of: "\"", with: "&quot;")` does not replace the quote mark. This allows you to break out of html attributes.

I believe replacingOccurences takes an optional third parameter that allows you to specify options to make it work on UTF-8 characters instead of grapheme clusters, which would be a good fix for this issue.

I see depending on version, leafkit might use `replacing` instead of `replacingOccurences`. I don't know swift that well and couldn't find docs on what replacing does, so I don't know if both versions of the function are affected. The version of swift i was testing on I believe was using replacingOccurences

It seems like replacingOccurences will skip past prefix characters of extended grapheme clusters, which is what would be needed in order to meaningfully bypass esaping of <. Thus i think this is mostly limited to attributes and not general text.

### PoC

An example vapor application that is vulnerable might look like

routes.swift
```swift
import Vapor

struct Hello: Content {
    var msg: String?
}

func routes(_ app: Application) throws {
    app.post { req throws in
	let Hello = try req.content.decode(Hello.self)
        return req.view.render("hello", [
            "msg": Hello.msg ?? "Hello World!"
        ])
    }
}
```

With a hello.leaf that looks like
```
<div title="#(msg)">Hover to see message</div>
```

And then you POST something like `msg=%22%cc%81=1%20autofocus%20tabindex=0%20onfocus=alert(1)%20`

### Impact
If a website uses leaf to escape an attribute value based on user input, the attacker may be able to insert a malicious attribute. If a site is not using a secure CSP policy, then this can be used to execute malicious javascript (XSS). Impact is context dependent if a site is using a secure CSP policy.

## References
- https://github.com/vapor/leaf-kit/security/advisories/GHSA-4hfh-fch3-5q7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-27120
- https://github.com/vapor/leaf-kit/commit/8919e39476c3a4ba05c28b71546bb9195f87ef34
- https://github.com/vapor/leaf-kit
