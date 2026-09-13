# [M] ReDOS vulnerabities: multiple grammars

## Summary
Severity: Medium
Advisory: GHSA-7wwv-vh3v-89cq
CWE: CWE-20, CWE-400
Ecosystem: npm
Published: 2020-12-04
Source: https://github.com/advisories/GHSA-7wwv-vh3v-89cq
Type: github-advisory

## Affected
- npm: `highlight.js` — affected >=9.0.0 <10.4.1
- npm: `@highlightjs/cdn-assets` — affected >=0 <10.4.1

## Details
### Impact: Potential ReDOS vulnerabilities (exponential and polynomial RegEx backtracking)

[oswasp](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS): 

> The Regular expression Denial of Service (ReDoS) is a Denial of Service attack, that exploits the fact that most Regular Expression implementations may reach extreme situations that cause them to work very slowly (exponentially related to input size). An attacker can then cause a program using a Regular Expression to enter these extreme situations and then hang for a very long time.

If are you are using Highlight.js to highlight user-provided data you are possibly vulnerable.  On the client-side (in a browser or Electron environment) risks could include lengthy freezes or crashes... On the server-side infinite freezes could occur... effectively preventing users from accessing your app or service (ie, Denial of Service).

This is an issue with grammars shipped with the parser (and potentially 3rd party grammars also), not the parser itself. If you are using Highlight.js with any of the following grammars you are vulnerable.  If you are using `highlightAuto` to detect the language (and have any of these grammars registered) you are vulnerable. Exponential grammars (C, Perl, JavaScript) are auto-registered when using the common grammar subset/library `require('highlight.js/lib/common')` as of 10.4.0 - see https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@10.4.0/build/highlight.js

All versions prior to 10.4.1 are vulnerable, including version 9.18.5. 

**Grammars with exponential backtracking issues:**

  - c-like (c, cpp, arduino)
  - handlebars (htmlbars)
  - gams
  - perl
  - jboss-cli
  - r
  - erlang-repl
  - powershell
  - routeros
  - livescript (10.4.0 and 9.18.5 included this fix)
  - javascript & typescript (10.4.0 included partial fixes)

And of course any aliases of those languages have the same issue. ie: `hpp` is no safer than `cpp`.

**Grammars with polynomial backtracking issues:**

- kotlin
- gcode
- d
- aspectj
- moonscript
- coffeescript/livescript
- csharp
- scilab
- crystal
- elixir
- basic
- ebnf
- ruby
- fortran/irpf90
- livecodeserver
- yaml
- x86asm
- dsconfig
- markdown
- ruleslanguage
- xquery
- sqf

And again: any aliases of those languages have the same issue. ie: `ruby` and `rb` share the same ruby issues.


### Patches

- Version 10.4.1 resolves these vulnerabilities.  Please upgrade.

### Workarounds / Mitigations

- Discontinue use the affected grammars. (or perhaps use only those with poly vs exponential issues)
- Attempt cherry-picking the grammar fixes into older versions...
- Attempt using newer CDN versions of any affected languages.  (ie using an older CDN version of the library with newer CDN grammars).  Your mileage may vary.

### References

- https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS

### For more information

If you have any questions or comments about this advisory:
* Open an issue: https://github.com/highlightjs/highlight.js/issues
* Email us at [security@highlightjs.com](mailto:security@highlightjs.com)

## References
- https://github.com/highlightjs/highlight.js/security/advisories/GHSA-7wwv-vh3v-89cq
- https://github.com/highlightjs/highlight.js/commit/373b9d862401162e832ce77305e49b859e110f9c
- https://www.npmjs.com/package/@highlightjs/cdn-assets
- https://www.npmjs.com/package/highlight.js
