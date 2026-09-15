# [M] fast-jwt has a ReDoS when using RegExp in allowed* leading to CPU exhaustion during token verification

## Summary
Severity: Medium
Advisory: GHSA-cjw9-ghj4-fwxf
CVE: CVE-2026-35041
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-cjw9-ghj4-fwxf
Type: github-advisory

## Affected
- npm: `fast-jwt` — affected >=5.0.0 <6.2.1

## Details
## ⚠️ IMPORTANT CLARIFICATIONS

  ### Affected Configurations
  This vulnerability ONLY affects applications that:
  - Use RegExp objects (not strings) in the allowedAud, allowedIss, allowedSub, allowedJti, or allowedNonce options
  - Configure patterns susceptible to catastrophic backtracking
  - Example: `allowedAud: /^(a+)+X$/` ← VULNERABLE
  - Example: `allowedAud: "api.company.com"` ← SAFE

  ### Not Affected
  - Applications using string patterns for audience validation (most common)
  - Applications using safe RegExp patterns without nested quantifiers
  - Default fast-jwt configurations

  ### Assessment Guide
  To determine if you're affected:
  1. Check ifallowedAud, allowedIss, allowedSub, allowedJti, or allowedNonce use RegExp objects (`/pattern/` or `new RegExp()`)
  2. If yes, review the pattern for nested quantifiers like `(a+)+`, `(.*)*`, etc.
  3. If no RegExp usage, you are NOT affected

------

<html>
<body>
<!--StartFragment--><h2 data-start="218" data-end="228">Summary</h2>
<p data-start="230" data-end="364">A denial-of-service condition exists in <code data-start="270" data-end="280">fast-jwt</code> when the <code data-start="290" data-end="302">allowedAud</code> verification option is configured using a regular expression.</p>
<p data-start="366" data-end="618">Because the <code data-start="378" data-end="383">aud</code> claim is attacker-controlled and the library evaluates it against the supplied <code data-start="463" data-end="471">RegExp</code>, a crafted JWT can trigger catastrophic backtracking in the JavaScript regex engine, resulting in significant CPU consumption during verification.</p>
<p data-start="620" data-end="726">This occurs with a <strong data-start="639" data-end="661">validly signed JWT</strong>, making the issue exploitable in authenticated contexts such as:</p>
<ul data-start="728" data-end="855">
<li data-start="728" data-end="744">
<p data-start="730" data-end="744">API gateways</p>
</li>
<li data-start="745" data-end="774">
<p data-start="747" data-end="774">authentication middleware</p>
</li>
<li data-start="775" data-end="811">
<p data-start="777" data-end="811">service-to-service communication</p>
</li>
<li data-start="812" data-end="855">
<p data-start="814" data-end="855">OAuth / OIDC token validation pipelines</p>
</li>
</ul>
<hr data-start="857" data-end="860">
<h2 data-start="862" data-end="883">Affected Component</h2>
<ul data-start="885" data-end="1035">
<li data-start="885" data-end="910">
<p data-start="887" data-end="910"><strong data-start="887" data-end="899">Library:</strong> fast-jwt</p>
</li>
<li data-start="911" data-end="940">
<p data-start="913" data-end="940"><strong data-start="913" data-end="932">Version tested:</strong> 6.1.0</p>
</li>
<li data-start="941" data-end="974">
<p data-start="943" data-end="974"><strong data-start="943" data-end="955">Runtime:</strong> Node.js v24.13.1</p>
</li>
<li data-start="975" data-end="1035">
<p data-start="977" data-end="1035"><strong data-start="977" data-end="989">Feature:</strong> claim validation using <code data-start="1013" data-end="1033">allowedAud: RegExp</code></p>
</li>
</ul>
<hr data-start="1037" data-end="1040">
<h2 data-start="1042" data-end="1051">Impact</h2>
<p data-start="1053" data-end="1091"><strong data-start="1053" data-end="1091">CPU exhaustion / Denial of Service</strong></p>
<p data-start="1093" data-end="1203">A crafted JWT causes verification to take multiple seconds per request due to catastrophic regex backtracking.</p>
<h3 data-start="1205" data-end="1236">Measured verification times</h3>
<div class="TyagGW_tableContainer"><div tabindex="-1" class="group TyagGW_tableWrapper flex flex-col-reverse w-fit">
Input size (n) | Verification time
-- | --
24 | ~123 ms
28 | ~1.97 s
30 | ~7.85 s

</div></div>
<p data-start="1339" data-end="1361">This is sufficient to:</p>
<ul data-start="1363" data-end="1546">
<li data-start="1363" data-end="1399">
<p data-start="1365" data-end="1399">block Node.js event loop threads</p>
</li>
<li data-start="1400" data-end="1426">
<p data-start="1402" data-end="1426">degrade API throughput</p>
</li>
<li data-start="1427" data-end="1463">
<p data-start="1429" data-end="1463">cause cascading service failures</p>
</li>
<li data-start="1464" data-end="1503">
<p data-start="1466" data-end="1503">increase serverless execution costs</p>
</li>
<li data-start="1504" data-end="1546">
<p data-start="1506" data-end="1546">saturate authentication infrastructure</p>
</li>
</ul>
<hr data-start="1548" data-end="1551">
<h2 data-start="1553" data-end="1566">Root Cause</h2>
<p data-start="1568" data-end="1627">The library allows regular expressions in claim validation:</p>
<pre class="overflow-visible! px-0!" data-start="1629" data-end="1661"><div class="w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border corner-superellipse/1.1 border-token-border-light bg-token-bg-elevated-secondary rounded-3xl"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="pointer-events-none absolute inset-x-px top-0 bottom-96"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-bg-elevated-secondary"></div></div></div><div class="corner-superellipse/1.1 rounded-3xl bg-token-bg-elevated-secondary"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼo">allowedAud</span><span>: </span><span class="ͼk">/^(a+)+X$/</span></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>
<p data-start="1663" data-end="1702">The <code data-start="1667" data-end="1672">aud</code> claim is attacker-controlled:</p>
<pre class="overflow-visible! px-0!" data-start="1704" data-end="1739"><div class="w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border corner-superellipse/1.1 border-token-border-light bg-token-bg-elevated-secondary rounded-3xl"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="pointer-events-none absolute inset-x-px top-0 bottom-96"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-bg-elevated-secondary"></div></div></div><div class="corner-superellipse/1.1 rounded-3xl bg-token-bg-elevated-secondary"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼm">aud</span><span> </span><span class="ͼg">=</span><span> </span><span class="ͼk">"a"</span><span class="ͼg">.</span><span>repeat(</span><span class="ͼm">n</span><span>) </span><span class="ͼg">+</span><span> </span><span class="ͼk">"Y"</span></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>
<p data-start="1741" data-end="1811">This creates catastrophic backtracking in the JavaScript regex engine.</p>
<p data-start="1813" data-end="1881">Verification time grows <strong data-start="1837" data-end="1854">exponentially</strong> as input length increases.</p>
<hr data-start="1883" data-end="1886">
<h2 data-start="1888" data-end="1905">Exploitability</h2>
<p data-start="1907" data-end="1923">Attack requires:</p>
<ul data-start="1925" data-end="2066">
<li data-start="1925" data-end="1975">
<p data-start="1927" data-end="1975">a valid signed JWT (post-authentication context)</p>
</li>
<li data-start="1976" data-end="2015">
<p data-start="1978" data-end="2015">attacker control over the <code data-start="2004" data-end="2009">aud</code> claim</p>
</li>
<li data-start="2016" data-end="2066">
<p data-start="2018" data-end="2066">a vulnerable regex configured by the application</p>
</li>
</ul>
<h3 data-start="2068" data-end="2099">Common real-world scenarios</h3>
<ul data-start="2101" data-end="2232">
<li data-start="2101" data-end="2120">
<p data-start="2103" data-end="2120">shared HS secrets</p>
</li>
<li data-start="2121" data-end="2144">
<p data-start="2123" data-end="2144">internal JWT issuance</p>
</li>
<li data-start="2145" data-end="2174">
<p data-start="2147" data-end="2174">microservice authentication</p>
</li>
<li data-start="2175" data-end="2206">
<p data-start="2177" data-end="2206">OAuth / OIDC custom audiences</p>
</li>
<li data-start="2207" data-end="2232">
<p data-start="2209" data-end="2232">internal service tokens</p>
</li>
</ul>
<hr data-start="2234" data-end="2237">
<h2 data-start="2239" data-end="2258">Proof of Concept</h2>
<h3 data-start="2260" data-end="2282">Reproduction steps</h3>
<ol data-start="2284" data-end="2407">
<li data-start="2284" data-end="2305">
<p data-start="2287" data-end="2305">Install <code data-start="2295" data-end="2305">fast-jwt</code></p>
</li>
<li data-start="2306" data-end="2357">
<p data-start="2309" data-end="2357">Configure verifier with a RegExp in <code data-start="2345" data-end="2357">allowedAud</code></p>
</li>
<li data-start="2358" data-end="2407">
<p data-start="2361" data-end="2407">Send a valid signed JWT with adversarial <code data-start="2402" data-end="2407">aud</code></p>
</li>
</ol>
<h3 data-start="2409" data-end="2431">Attached artifacts</h3>
<ul data-start="2433" data-end="2495">
<li data-start="2433" data-end="2463">
<p data-start="2435" data-end="2463"><code data-start="2435" data-end="2463">poc-suite-redos-fastjwt.js</code></p>
</li>
<li data-start="2464" data-end="2495">
<p data-start="2466" data-end="2495"><code data-start="2466" data-end="2495">evidence-redos-fastjwt.json</code></p>
</li>
</ul>
<h3 data-start="2497" data-end="2518">Observed behavior</h3>
<p data-start="2520" data-end="2612">Verification CPU time increases from milliseconds to multiple seconds as input length grows.</p>
<hr data-start="2614" data-end="2617">
<h2 data-start="2619" data-end="2645">Security Classification</h2>
<ul data-start="2647" data-end="2793">
<li data-start="2647" data-end="2695">
<p data-start="2649" data-end="2695"><strong data-start="2649" data-end="2662">CWE-1333:</strong> Inefficient Regular Expression</p>
</li>
<li data-start="2696" data-end="2746">
<p data-start="2698" data-end="2746"><strong data-start="2698" data-end="2710">CWE-400:</strong> Uncontrolled Resource Consumption</p>
</li>
<li data-start="2747" data-end="2793">
<p data-start="2749" data-end="2793"><strong data-start="2749" data-end="2759">Class:</strong> Authenticated Denial of Service</p>
</li>
</ul>
<hr data-start="2795" data-end="2798">
<h2 data-start="2800" data-end="2820">Expected Behavior</h2>
<p data-start="2822" data-end="2898">The library should prevent unbounded CPU work on attacker-controlled claims.</p>
<h3 data-start="2900" data-end="2924">Possible mitigations</h3>
<ul data-start="2926" data-end="3092">
<li data-start="2926" data-end="2949">
<p data-start="2928" data-end="2949">safe-regex validation</p>
</li>
<li data-start="2950" data-end="2989">
<p data-start="2952" data-end="2989">maximum length enforcement for claims</p>
</li>
<li data-start="2990" data-end="3015">
<p data-start="2992" data-end="3015">regex complexity limits</p>
</li>
<li data-start="3016" data-end="3092">
<p data-start="3018" data-end="3092">documentation warning about ReDoS risks when using RegExp-based validation</p>
</li>
</ul>
<hr data-start="3094" data-end="3097">
<h2 data-start="3099" data-end="3107">Notes</h2>
<p data-start="3109" data-end="3215">Signature verification occurs before claim validation, therefore this is <strong data-start="3182" data-end="3214">not a pre-authentication DoS</strong>.</p>
<p data-start="3217" data-end="3360">However, the vulnerability remains exploitable in authenticated or token-bearing contexts and can significantly impact production environments.</p><!--EndFragment-->
</body>
</html>

## References
- https://github.com/nearform/fast-jwt/security/advisories/GHSA-cjw9-ghj4-fwxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-35041
- https://github.com/nearform/fast-jwt/pull/595
- https://github.com/nearform/fast-jwt/commit/b0be0ca161593836a153d5180ca5358ad9b5de94
- https://github.com/nearform/fast-jwt
- https://github.com/nearform/fast-jwt/releases/tag/v6.2.1
