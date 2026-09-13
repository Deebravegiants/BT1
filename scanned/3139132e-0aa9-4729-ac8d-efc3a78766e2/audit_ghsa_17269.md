# [M] Picklescan is vulnerable to RCE through missing detection when calling numpy.f2py.crackfortran._eval_length

## Summary
Severity: Medium
Advisory: GHSA-6556-fwc2-fg2p
CVE: CVE-2025-71339
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-6556-fwc2-fg2p
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.33

## Details
### Summary

Picklescan uses the `numpy.f2py.crackfortran._eval_length` function (a NumPy F2PY helper) to execute arbitrary Python code during unpickling.

### Details

Picklescan fails to detect a malicious pickle that uses the gadget `numpy.f2py.crackfortran._eval_length` in `__reduce__`, allowing arbitrary command execution when the pickle is loaded. A crafted object returns this function plus attacker‑controlled arguments; the scan reports the file as safe, but pickle.load() triggers execution.

### PoC
```python
class PoC:
    def __reduce__(self):
        from numpy.f2py.crackfortran import _eval_length
        return _eval_length, ("__import__('os').system('whoami')", None)
```

### Impact

- Arbitrary code execution on the victim machine once they load the “scanned as safe” pickle / model file.
- Affects any workflow relying on Picklescan to vet untrusted pickle / PyTorch artifacts.
- Enables supply‑chain poisoning of shared model files.

### Credits
- [ac0d3r](https://github.com/ac0d3r)
- [Tong Liu](https://lyutoon.github.io), Institute of information engineering, CAS

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-6556-fwc2-fg2p
- https://nvd.nist.gov/vuln/detail/CVE-2025-71339
- https://github.com/mmaitre314/picklescan/pull/53
- https://github.com/mmaitre314/picklescan/commit/70c1c6c31beb6baaf52c8db1b6c3c0e84a6f9dab
- https://github.com/advisories/GHSA-6556-fwc2-fg2p
- https://github.com/mmaitre314/picklescan
- https://github.com/mmaitre314/picklescan/releases/tag/v0.0.33
- https://github.com/pypa/advisory-database/tree/main/vulns/picklescan/PYSEC-2026-1783.yaml
- https://pypi.org/project/picklescan
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-numpy-f2py-crackfortran-eval-length-gadget
