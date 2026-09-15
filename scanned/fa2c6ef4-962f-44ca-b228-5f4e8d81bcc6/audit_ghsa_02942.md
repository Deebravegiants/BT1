# [M] Code injection in `saved_model_cli`

## Summary
Severity: Medium
Advisory: GHSA-3rcw-9p9x-582v
CVE: CVE-2021-41228
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-3rcw-9p9x-582v
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1

## Details
### Impact
TensorFlow's `saved_model_cli` tool is vulnerable to a code injection as it [calls `eval` on user supplied strings](https://github.com/tensorflow/tensorflow/blob/87462bfac761435a46641ff2f10ad0b6e5414a4b/tensorflow/python/tools/saved_model_cli.py#L524-L550)
  
```python
def preprocess_input_exprs_arg_string(input_exprs_str):
  ... 
  for input_raw in filter(bool, input_exprs_str.split(';')):
    ...
    input_key, expr = input_raw.split('=', 1)
    input_dict[input_key] = eval(expr)
  ...
``` 
  
This can be used by attackers to run arbitrary code on the plaform where the CLI tool runs.
However, given that the tool is always run manually, the impact of this is not severe. We have patched this by adding a `safe` flag which defaults to `True` and an explicit warning for users. 

### Patches
We have patched the issue in GitHub commit [8b202f08d52e8206af2bdb2112a62fafbc546ec7](https://github.com/tensorflow/tensorflow/commit/8b202f08d52e8206af2bdb2112a62fafbc546ec7).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Omer Kaspi from Vdoo.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-3rcw-9p9x-582v
- https://nvd.nist.gov/vuln/detail/CVE-2021-41228
- https://github.com/tensorflow/tensorflow/commit/8b202f08d52e8206af2bdb2112a62fafbc546ec7
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-637.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-835.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-420.yaml
- https://github.com/tensorflow/tensorflow
