# [M] Trix Editor Arbitrary Code Execution Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qjqp-xr96-cj99
CVE: CVE-2024-34341
CWE: CWE-79
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-07
Source: https://github.com/advisories/GHSA-qjqp-xr96-cj99
Type: github-advisory

## Affected
- npm: `trix` — affected >=2.0.0 <2.1.1
- npm: `trix` — affected >=0.9.0 <1.3.2
- RubyGems: `actiontext` — affected >=7.0.0.alpha1 <7.0.8.3
- RubyGems: `actiontext` — affected >=7.1.0.beta1 <7.1.3.3

## Details
The Trix editor, versions prior to 2.1.1, is vulnerable to arbitrary code execution when copying and pasting content from the web or other documents with markup into the editor. The vulnerability stems from improper sanitization of pasted content, allowing an attacker to embed malicious scripts which are executed within the context of the application.

**Vulnerable Versions**: 

- 1.x series up to and including 1.3.1
- 2.x series up to and including 2.1.0

**Fixed Versions**: 

- v1.3.2
- v2.1.1

**Vector**:

- **Bug 1**: When copying content manipulated by a script, such as:

```js
document.addEventListener('copy', function(e){
  e.clipboardData.setData('text/html', '<div><noscript><div class="123</noscript>456<img src=1 onerror=alert(1)//"></div></noscript></div>');
  e.preventDefault();
});
```

and pasting into the Trix editor, the script within the content is executed.

- **Bug 2**: Similar execution occurs with content structured as:

```js
document.write(`copy<div data-trix-attachment="{&quot;contentType&quot;:&quot;text/html&quot;,&quot;content&quot;:&quot;&lt;img src=1 onerror=alert(101)&gt;HELLO123&quot;}"></div>me`);
```

### Impact:
An attacker could exploit these vulnerabilities to execute arbitrary JavaScript code within the context of the user's session, potentially leading to unauthorized actions being performed or sensitive information being disclosed.

### Remediation:

**Update Recommendation**: Users should upgrade to Trix editor version 2.1.1 or later, which incorporates proper sanitization of input from copied content.

**CSP Enhancement**: Additionally, enhancing the Content Security Policy (CSP) to disallow inline scripts can significantly mitigate the risk of such vulnerabilities. Set CSP policies such as script-src 'self' to ensure that only scripts hosted on the same origin are executed, and explicitly prohibit inline scripts using script-src-elem.

### References:
  - https://github.com/basecamp/trix/releases/tag/v2.1.1
  - https://github.com/basecamp/trix/pull/1147
  - https://github.com/basecamp/trix/pull/1149
  - https://github.com/basecamp/trix/pull/1153

**Credit**: These issues were reported by security researchers [loknop](https://hackerone.com/loknop) and [pinpie](https://hackerone.com/pinpie).

## References
- https://github.com/basecamp/trix/security/advisories/GHSA-qjqp-xr96-cj99
- https://nvd.nist.gov/vuln/detail/CVE-2024-34341
- https://github.com/basecamp/trix/pull/1147
- https://github.com/basecamp/trix/pull/1149
- https://github.com/basecamp/trix/commit/1a5c68a14d48421fc368e30026f4a7918028b7ad
- https://github.com/basecamp/trix/commit/841ff19b53f349915100bca8fcb488214ff93554
- https://github.com/rails/rails/commit/07e6c88cc4defe6f6b8d28e79eb13a518e15b14c
- https://github.com/rails/rails/commit/260cb392fc1ee91d0b749cff08d1c8d54b230bd3
- https://github.com/rails/rails/commit/73fac32511eefdd45d8f00fecc2b8cc5408ea6d5
- https://discuss.rubyonrails.org/t/xss-vulnerabilities-in-trix-editor/85803
- https://github.com/basecamp/trix
- https://github.com/basecamp/trix/releases/tag/v2.1.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actiontext/CVE-2024-34341.yml
- https://rubyonrails.org/2024/5/17/Rails-Versions-7-0-8-2-and-7-1-3-3-have-been-released
- https://rubyonrails.org/2024/5/17/Rails-Versions-7-0-8-3-has-been-released
