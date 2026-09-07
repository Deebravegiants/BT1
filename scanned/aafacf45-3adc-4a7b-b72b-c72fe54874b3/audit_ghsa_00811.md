# [H] Cross-Site Scripting in @progress/kendo-angular-editor

## Summary
Severity: High
Advisory: GHSA-j7wp-vjj6-cp5m
CWE: CWE-79
Ecosystem: npm
Published: 2020-08-11
Source: https://github.com/advisories/GHSA-j7wp-vjj6-cp5m
Type: github-advisory

## Affected
- npm: `@progress/kendo-angular-editor` — affected >=0 <1.2.3

## Details
Kendo UI for Angular Editor Component (npm package @progress/kendo-angular-editor) before version 1.2.3 is vulnerable to Cross-Site Scripting. When the Editor content contains potentially malicious scripts in element event handlers, they get executed.
Adding the following content to the Editor value demonstrates the issue: `<img src="" onerror=alert(document.domain)>`.

## References
- https://github.com/telerik/kendo-angular-editor
- https://stackblitz.com/edit/angular-6xzuzp-tef7lb?file=app/app.component.ts
- https://www.npmjs.com/advisories/1549
