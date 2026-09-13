# [C] rpc.py vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-8rq8-f485-7v8x
CVE: CVE-2022-35411
CWE: CWE-502, CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-09
Source: https://github.com/advisories/GHSA-8rq8-f485-7v8x
Type: github-advisory

## Affected
- PyPI: `rpc.py` — affected >=0.4.2

## Details
rpc.py through 0.6.0 allows Remote Code Execution because an unpickle occurs when the "serializer: pickle" HTTP header is sent. In other words, although JSON (not Pickle) is the default data format, an unauthenticated client can cause the data to be processed with unpickle.

[Per the maintainer](https://github.com/abersheeran/rpc.py/issues/22), rpc.py is not designed for an API that is open to the outside world, and external requests cannot reach rpc.py in real world use.

A [fix](https://github.com/abersheeran/rpc.py/commit/491e7a841ed9a754796d6ab047a9fb16e23bf8bd) exists on the `master` branch. As a workaround, use the following code to turn off pickle in older versions:
```
del SERIALIZER_NAMES[PickleSerializer.name]
del SERIALIZER_TYPES[PickleSerializer.content_type]

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35411
- https://github.com/abersheeran/rpc.py/issues/22
- https://github.com/abersheeran/rpc.py/commit/491e7a841ed9a754796d6ab047a9fb16e23bf8bd
- https://github.com/abersheeran/rpc.py
- https://github.com/ehtec/rpcpy-exploit
- https://medium.com/%40elias.hohl/remote-code-execution-0-day-in-rpc-py-709c76690c30
- https://medium.com/@elias.hohl/remote-code-execution-0-day-in-rpc-py-709c76690c30
- http://packetstormsecurity.com/files/167872/rpc.py-0.6.0-Remote-Code-Execution.html
