# [M] @webiny/react-rich-text-renderer vulnerable to insecure rendering of rich text content

## Summary
Severity: Medium
Advisory: GHSA-3x59-vrmc-5mx6
CVE: CVE-2023-41167
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-24
Source: https://github.com/advisories/GHSA-3x59-vrmc-5mx6
Type: github-advisory

## Affected
- npm: `@webiny/react-rich-text-renderer` — affected >=0 <5.37.2

## Details
## Overview
`@webiny/react-rich-text-renderer` is a react component to render data coming from Webiny Headless CMS and Webiny Form Builder. The `@webiny/react-rich-text-renderer` package depends on the [editor.js](https://editorjs.io/) rich text editor to handle rich text content. The CMS stores rich text content from the `editor.js` into the database. When the `@webiny/react-rich-text-renderer` is used to render such content, it uses the `dangerouslySetInnerHTML` prop, without applying HTML sanitization. The issue arises when an actor, who in this context would specifically be a content manager with access to the CMS, inserts a malicious script as part of the user-defined input. This script is then injected and executed within the user's browser when the main page or admin page loads.

## Am I affected?
You will be affected if you're running a Webiny project created prior to `5.35.0` and you're using the legacy rich text editor (which uses `editor.js` library under the hood). If you've already switched to using the new rich text editor, powered by Lexical editor, you will not be affected by this.

## How do I patch this vulnerability?
Update to Webiny version `5.37.2`.

## References
- https://github.com/webiny/webiny-js/security/advisories/GHSA-3x59-vrmc-5mx6
- https://nvd.nist.gov/vuln/detail/CVE-2023-41167
- https://github.com/webiny/webiny-js/commit/8748bc53fe862bb03d4459ccc0be39084a5d35c0
- https://github.com/webiny/webiny-js
- https://webiny.com
