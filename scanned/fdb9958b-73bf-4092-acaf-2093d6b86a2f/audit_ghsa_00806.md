# [M] XSS via JQLite DOM manipulation functions in AngularJS

## Summary
Severity: Medium
Advisory: GHSA-5cp4-xmrw-59wf
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-08-05
Source: https://github.com/advisories/GHSA-5cp4-xmrw-59wf
Type: github-advisory

## Affected
- npm: `angular` — affected >=0 <1.8.0

## Details
### Summary
XSS may be triggered in AngularJS applications that sanitize user-controlled HTML snippets before passing them to `JQLite` methods like `JQLite.prepend`, `JQLite.after`, `JQLite.append`, `JQLite.replaceWith`, `JQLite.append`, `new JQLite` and `angular.element`.

### Description

JQLite (DOM manipulation library that's part of AngularJS) manipulates input HTML before inserting it to the DOM in `jqLiteBuildFragment`.

One of the modifications performed [expands an XHTML self-closing tag](https://github.com/angular/angular.js/blob/418355f1cf9a9a9827ae81d257966e6acfb5623a/src/jqLite.js#L218).

If `jqLiteBuildFragment` is called (e.g. via `new JQLite(aString)`) with user-controlled HTML string that was sanitized (e.g. with [DOMPurify](https://github.com/cure53/DOMPurify)), the transformation done by JQLite may modify some forms of an inert, sanitized payload into a payload containing JavaScript - and trigger an XSS when the payload is inserted into DOM.

This is similar to a bug in jQuery `htmlPrefilter` function that was [fixed in 3.5.0](https://blog.jquery.com/2020/04/10/jquery-3-5-0-released/).

### Proof of concept

```javascript
const inertPayload = `<div><style><style/><img src=x onerror="alert(1337)"/>` 
```
Note that the style element is not closed and `<img` would be a text node inside the style if inserted into the DOM as-is.
As such, some HTML sanitizers would leave the `<img` as is without processing it and stripping the `onerror` attribute.

```javascript
angular.element(document).append(inertPayload);
```
This will alert, as `<style/>` will be replaced with `<style></style>` before adding it to the DOM, closing the style element early and reactivating `img`.

### Patches
The issue is patched in `JQLite` bundled with angular 1.8.0. AngularJS users using JQuery should upgrade JQuery to 3.5.0, as a similar vulnerability [affects jQuery <3.5.0](https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2).

### Workarounds
Changing sanitizer configuration not to allow certain tag grouping (e.g. `<option><style></option>`) or inline style elements may stop certain exploitation vectors, but it's uncertain if all possible exploitation vectors would be covered. Upgrade of AngularJS to 1.8.0 is recommended.

### References
https://github.com/advisories/GHSA-mhp6-pxh8-r675
https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2
https://github.com/jquery/jquery/security/advisories/GHSA-jpcq-cgw6-v4j6
https://blog.jquery.com/2020/04/10/jquery-3-5-0-released/
https://snyk.io/vuln/SNYK-JS-ANGULAR-570058

## References
- https://github.com/google/security-research/security/advisories/GHSA-5cp4-xmrw-59wf
- https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2
- https://github.com/jquery/jquery/security/advisories/GHSA-jpcq-cgw6-v4j6
- https://blog.jquery.com/2020/04/10/jquery-3-5-0-released
- https://github.com/advisories/GHSA-mhp6-pxh8-r675
- https://github.com/angular/angular.js
- https://snyk.io/vuln/SNYK-JS-ANGULAR-570058
