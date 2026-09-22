# [C] Incomplete validation in boosted trees code

## Summary
Severity: Critical
Advisory: GHSA-57wx-m983-2f88
CVE: CVE-2021-41208
CWE: CWE-476, CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-57wx-m983-2f88
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
The [code for boosted trees in TensorFlow](https://github.com/tensorflow/tensorflow/blob/e0b6e58c328059829c3eb968136f17aa72b6c876/tensorflow/core/kernels/boosted_trees/stats_ops.cc) is still missing validation. As a result, attackers can trigger denial of service (via dereferencing `nullptr`s or via `CHECK`-failures) as well as abuse undefined behavior (binding references to `nullptr`s). An attacker can also read and write from heap buffers, depending on the API that gets used and the arguments that are passed to the call.

**Note**: Given that the boosted trees implementation in TensorFlow is unmaintained, it is recommend to no longer use these APIs.  Instead, please use the downstream [TensorFlow Decision Forests](https://github.com/tensorflow/decision-forests) project which is newer and supports more features. We will deprecate TensorFlow's boosted trees APIs in subsequent releases.

### Patches
We have patched the issue in GitHub commit [5c8c9a8bfe750f9743d0c859bae112060b216f5c](https://github.com/tensorflow/tensorflow/commit/5c8c9a8bfe750f9743d0c859bae112060b216f5c).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-57wx-m983-2f88
- https://nvd.nist.gov/vuln/detail/CVE-2021-41208
- https://github.com/tensorflow/tensorflow/commit/5c8c9a8bfe750f9743d0c859bae112060b216f5c
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-617.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-815.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-400.yaml
- https://github.com/tensorflow/tensorflow
