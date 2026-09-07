# [M] DOM Clobbering Gadget found in astro's client-side router that leads to XSS

## Summary
Severity: Medium
Advisory: GHSA-m85w-3h95-hcf9
CVE: CVE-2024-47885
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-m85w-3h95-hcf9
Type: github-advisory

## Affected
- npm: `astro` — affected >=3.0.0 <4.16.1

## Details
### Summary

A DOM Clobbering gadget has been discoverd in Astro's client-side router. It can lead to cross-site scripting (XSS) in websites enables Astro's client-side routing and has *stored* attacker-controlled scriptless HTML elements (i.e., `iframe` tags with unsanitized `name` attributes) on the destination pages.

### Details

#### Backgrounds

DOM Clobbering is a type of code-reuse attack where the attacker first embeds a piece of non-script, seemingly benign HTML markups in the webpage (e.g. through a post or comment) and leverages the gadgets (pieces of js code) living in the existing javascript code to transform it into executable code. More for information about DOM Clobbering, here are some references:

[1] https://scnps.co/papers/sp23_domclob.pdf
[2] https://research.securitum.com/xss-in-amp4email-dom-clobbering/


#### Gadgets found in Astro

We identified a DOM Clobbering gadget in Astro's client-side routing module, specifically in the `<ViewTransitions />` component. When integrated, this component introduces the following vulnerable code, which is executed during page transitions (e.g., clicking an `<a>` link):

https://github.com/withastro/astro/blob/7814a6cad15f06931f963580176d9b38aa7819f2/packages/astro/src/transitions/router.ts#L135-L156

However, this implementation is vulnerable to a DOM Clobbering attack. The `document.scripts` lookup can be shadowed by an attacker injected non-script HTML elements (e.g., `<img name="scripts"><img name="scripts">`) via the browser's named DOM access mechanism. This manipulation allows an attacker to replace the intended script elements with an array of attacker-controlled scriptless HTML elements. 

The condition `script.dataset.astroExec === ''` on line 138 can be bypassed because the attacker-controlled element does not have a data-astroExec attribute. Similarly, the check on line 134 can be bypassed as the element does not require a `type` attribute.

Finally, the `innerHTML` of an attacker-injected non-script HTML elements, which is plain text content before, will be set to the `.innerHTML` of an script element that leads to XSS.


### PoC

Consider a web application using Astro as the framework with client-side routing enabled and allowing users to embed certain scriptless HTML elements (e.g., `form` or `iframe`). This can be done through a bunch of website's feature that allows users to embed certain script-less HTML (e.g., markdown renderers, web email clients, forums) or via an HTML injection vulnerability in third-party JavaScript loaded on the page.

For PoC website, please refer to: `https://stackblitz.com/edit/github-4xgj2d`. Clicking the "about" button in the menu will trigger an `alert(1)` from an attacker-injected `form` element.

```
---
import Header from "../components/Header.astro";
import Footer from "../components/Footer.astro";
import { ViewTransitions } from "astro:transitions";
import "../styles/global.css";
const { pageTitle } = Astro.props;
---
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width" />
    <meta name="generator" content={Astro.generator} />
    <title>{pageTitle}</title>
    <ViewTransitions />
  </head>
  <body>
    <!--USER INPUT-->
    <iframe name="scripts">alert(1)</iframe>
    <iframe name="scripts">alert(1)</iframe>
    <!--USER INPUT-->
    
    <Header />
    <h1>{pageTitle}</h1>
    <slot />
    <Footer />
    <script>
      import "../scripts/menu.js";
    </script>
  </body>
</html>
```

### Impact

This vulnerability can result in cross-site scripting (XSS) attacks on websites that built with Astro that enable the client-side routing with `ViewTransitions` and store the user-inserted scriptless HTML tags without properly sanitizing the `name` attributes on the page.

### Patch

We recommend replacing `document.scripts` with `document.getElementsByTagName('script')` for referring to script elements. This will mitigate the possibility of DOM Clobbering attacks leveraging the `name` attribute.

### Reference

Similar issues for reference:
+ Webpack ([CVE-2024-43788](https://github.com/webpack/webpack/security/advisories/GHSA-4vvj-4cpr-p986))
+ Vite ([CVE-2024-45812](https://github.com/vitejs/vite/security/advisories/GHSA-64vr-g452-qvp3))
+ layui ([CVE-2024-47075](https://github.com/layui/layui/security/advisories/GHSA-j827-6rgf-9629))

## References
- https://github.com/withastro/astro/security/advisories/GHSA-m85w-3h95-hcf9
- https://nvd.nist.gov/vuln/detail/CVE-2024-47885
- https://github.com/withastro/astro/commit/a4ffbfaa5cb460c12bd486fd75e36147f51d3e5e
- https://github.com/withastro/astro
- https://github.com/withastro/astro/blob/7814a6cad15f06931f963580176d9b38aa7819f2/packages/astro/src/transitions/router.ts#L135-L156
