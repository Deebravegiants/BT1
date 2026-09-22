# [H] Scriban: Template Writes to Arbitrary CLR Properties via `TypedObjectAccessor` (Mass Assignment + `private` / `init` / `internal` Setter Bypass)

## Summary
Severity: High
Advisory: GHSA-7jvp-hj45-2f2m
CWE: CWE-284, CWE-915
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-7jvp-hj45-2f2m
Type: github-advisory

## Affected
- NuGet: `Scriban` — affected >=0 <7.2.2

## Details
<!-- obsidian --><h2 data-heading="Description">Description</h2>
<p>When a host pushes a CLR object into a Scriban <code>TemplateContext</code> via the standard, documented pattern —</p>
<pre><code class="language-csharp">var so = new ScriptObject();
so["user"] = currentUser;   // direct CLR reference
context.PushGlobal(so);
</code></pre>
<p>— <code>TypedObjectAccessor</code> exposes every public-getter property for <strong>both reading and writing</strong>, and writes land on the live host object and <strong>persist after <code>Render()</code> returns</strong>. The write path performs no <code>CanWrite</code> and no setter-visibility check, producing two related but distinct weaknesses:</p>
<p><strong>(A) Mass assignment of public setters — CWE-915 (originally F-002).</strong> Any <code>{ get; set; }</code> property is writable from template code (<code>{{ user.is_admin = true }}</code>, <code>{{ order.total_price = 0 }}</code>). This is "surprising but technically consistent with the setter being public" — and crucially, Scriban offers <strong>no way to expose such a property read-only</strong>, because <code>MemberFilter</code> is read/write-symmetric.</p>
<p><strong>(B) Access-modifier bypass — CWE-284 (originally F-007).</strong> Properties the developer <strong>deliberately</strong> restricted are also writable, because reflection ignores C# accessibility:</p>

Declaration | Developer intent | Actual behavior
-- | -- | --
{ get; set; } | writable | writable (mass assignment — A)
{ get; private set; } | only the owning class writes | template writes freely
{ get; internal set; } | only the declaring assembly writes | template writes freely
{ get; init; } | immutable after construction (C# 9 language guarantee) | template writes freely post-construction


<p>The <code>init</code>-only post-construction write — the highest false-positive risk — was explicitly confirmed against the shipped 7.2.1 package.</p>
<h2 data-heading="Affected Versions">Affected Versions</h2>
<p>All releases that ship <code>TypedObjectAccessor</code> (<code>&#x3C;= 7.2.1</code>). <code>PrepareMembers</code> has used the getter-only filter since the accessor was introduced, and <code>TrySetValue</code> has never checked the setter. The <code>init</code> bypass applies on .NET 5+; <code>private set</code> / <code>internal set</code> apply on every supported runtime. No patched version exists.</p>
<h2 data-heading="Steps to Reproduce">Steps to Reproduce</h2>
<blockquote>
<p>Copy-paste. Run from the engagement root (the folder containing both <code>scriban/</code> and <code>reports/</code>).</p>
</blockquote>
<p><strong>Prereqs:</strong></p>
<pre><code class="language-bash">test -d scriban || { echo "scriban source missing"; exit 1; }
( command -v dotnet >/dev/null &#x26;&#x26; dotnet --list-sdks | grep -q '^10\.' ) \
  || ( "$HOME/.dotnet/dotnet" --list-sdks | grep -q '^10\.' ) \
  || { echo ".NET 10 SDK missing"; exit 1; }
export PATH="$HOME/.dotnet:$PATH"
</code></pre>
<p><strong>Run both PoCs (native):</strong></p>
<pre><code class="language-bash">( cd reports/f002/poc &#x26;&#x26; dotnet run -c Release )   # (A) public-setter mass assignment
( cd reports/f007/poc &#x26;&#x26; dotnet run -c Release )   # (B) private/internal/init bypass
</code></pre>
<p><strong>Docker fallback (no native SDK required):</strong></p>
<pre><code class="language-bash">docker run --rm -v "$PWD":/work -w /work/reports/f007/poc \
  mcr.microsoft.com/dotnet/sdk:10.0 bash -lc "dotnet run -c Release"
</code></pre>
<p><strong>Confirm the published package is affected (not just master):</strong> swap the <code>ProjectReference</code> in <code>reports/f007/poc/poc.csproj</code> for <code>&#x3C;PackageReference Include="Scriban" Version="7.2.1" /></code> and re-run — the four bypasses still succeed.</p>
<p>Each PoC prints <code>[1]</code> original CLR values, <code>[2]</code> template output (reads originals → writes → reads back), and <code>[3]</code> the <strong>C#-side</strong> read after <code>Render()</code> proving the live host object was permanently altered.</p>
<h2 data-heading="Remediation">Remediation</h2>
<p>Fixes are listed flat. Note that (B) has a clean, clearly-correct code fix; (A) requires a <em>new control</em> because public-setter writes are otherwise by-design.</p>
<ul>
<li><strong>Fix 1 — block restricted setters in <code>TrySetValue</code> (<code>TypedObjectAccessor.cs</code> L108–L123). Fixes (B).</strong> Before the L120 <code>SetValue</code>, require a public, non-<code>init</code> setter:
<pre><code class="language-csharp">var setM = propertyAccessor.GetSetMethod(nonPublic: false);
if (setM is null) return false;   // private / internal / protected setters
if (setM.ReturnParameter.GetRequiredCustomModifiers()
      .Any(m => m.FullName == "System.Runtime.CompilerServices.IsExternalInit"))
    return false;                 // init-only: setter IS public, so the IsExternalInit check is REQUIRED
</code></pre>
A plain <code>GetSetMethod(nonPublic:false) != null</code> check is <strong>not</strong> sufficient for <code>init</code> — the init setter is public; only the <code>IsExternalInit</code> modreq distinguishes it.</li>
<li><strong>Fix 2 — give hosts a read/write distinction (addresses (A)).</strong> Add a <code>MemberWriteFilter</code> on <code>TemplateContext</code> (separate from <code>MemberFilter</code>) and/or a <code>[ScriptMemberReadOnly]</code> attribute, and split <code>_members</code> into <code>_readableMembers</code> / <code>_writableMembers</code> in <code>PrepareMembers</code> (L126–L186). Public-settable mass assignment cannot be blocked without one of these, because <code>MemberFilter</code> is read/write-symmetric today.</li>
<li><strong>Fix 3 — restore read-only-by-default on <code>ScriptObject.Import</code> (<code>ScriptObjectExtensions.cs</code> L320–L324).</strong> Gate the Liquid-compatibility relaxation behind an explicit opt-in instead of removing write protection globally.</li>
<li><strong>Fix 4 — documentation (<code>site/docs/runtime/safe-runtime.md</code>).</strong> State explicitly that templates can write CLR properties via reflection (including <code>private</code>/<code>internal</code>/<code>init</code> setters), and that <code>MemberFilter</code> does not separate read from write.</li>
<li><strong>Fix 5 — regression tests (<code>src/Scriban.Tests/</code>).</strong> Assert <code>private set</code> / <code>internal set</code> / <code>init</code> are non-writable from templates, that <code>MemberWriteFilter</code> / <code>[ScriptMemberReadOnly]</code> gate writes, and that only public <code>set</code> is writable.</li>
</ul>
<h2 data-heading="References">References</h2>
<ul>
<li>Vulnerable write path (no setter check): <code>scriban/src/Scriban/Runtime/Accessors/TypedObjectAccessor.cs</code> L108–L123 (<code>TrySetValue</code>), sink at L120 <code>propertyAccessor.SetValue(target, context.ToObject(span, value, propertyAccessor.PropertyType));</code></li>
<li>Getter-only member filter: <code>TypedObjectAccessor.cs</code> L126–L186 (<code>PrepareMembers</code>), enumeration at L150, gate at L156; same <code>_members</code> consumed by <code>TryGetValue</code> (L66–L83)</li>
<li>Member-assignment dispatch: <code>scriban/src/Scriban/ScribanAsync.generated.cs:2297</code> (<code>accessor.TrySetValue(...)</code>) and the synchronous evaluator</li>
<li>No read/write separation: <code>MemberFilter</code> declared <code>TemplateContext.cs:286</code>, applied <code>TemplateContext.cs:1026</code>; <code>ScriptObject.Import</code> read-only removal <code>ScriptObjectExtensions.cs:320–324</code></li>
<li>.NET reflection bypasses access modifiers: <a href="https://learn.microsoft.com/dotnet/api/system.reflection.propertyinfo.setvalue" class="external-link" target="_blank" rel="noopener nofollow">https://learn.microsoft.com/dotnet/api/system.reflection.propertyinfo.setvalue</a></li>
<li><code>init</code> accessors (C# 9): <a href="https://learn.microsoft.com/dotnet/csharp/language-reference/proposals/csharp-9.0/init" class="external-link" target="_blank" rel="noopener nofollow">https://learn.microsoft.com/dotnet/csharp/language-reference/proposals/csharp-9.0/init</a></li>
<li>CWE-915 — <a href="https://cwe.mitre.org/data/definitions/915.html" class="external-link" target="_blank" rel="noopener nofollow">https://cwe.mitre.org/data/definitions/915.html</a></li>
<li>CWE-284 — <a href="https://cwe.mitre.org/data/definitions/284.html" class="external-link" target="_blank" rel="noopener nofollow">https://cwe.mitre.org/data/definitions/284.html</a></li>
</ul>

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-7jvp-hj45-2f2m
- https://github.com/scriban/scriban
