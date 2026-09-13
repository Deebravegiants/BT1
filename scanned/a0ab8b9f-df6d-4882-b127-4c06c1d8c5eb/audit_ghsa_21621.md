# [C] NULL Pointer Dereference and Access of Uninitialized Pointer in TensorFlow

## Summary
Severity: Critical
Advisory: GHSA-h6gw-r52c-724r
CWE: CWE-476, CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-h6gw-r52c-724r
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact 
The [code for boosted trees in TensorFlow](https://github.com/tensorflow/tensorflow/blob/e0b6e58c328059829c3eb968136f17aa72b6c876/tensorflow/core/kernels/boosted_trees/stats_ops.cc) is still missing validation. This allows malicious users to read and write outside of bounds of heap allocated data as well as trigger denial of service (via dereferencing `nullptr`s or via `CHECK`-failures).

This follows after CVE-2021-41208 where these APIs were still vulnerable to multiple security issues.

**Note**: Given that the boosted trees implementation in TensorFlow is unmaintained, it is recommend to no longer use these APIs.  Instead, please use the downstream [TensorFlow Decision Forests](https://github.com/tensorflow/decision-forests) project which is newer and supports more features. 
  
These APIs are now deprecated in TensorFlow 2.8. We will remove TensorFlow's boosted trees APIs in subsequent releases.
  
### Patches
We have patched the known issues in multiple GitHub commits.
  
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

This should allow users to use existing boosted trees APIs for a while until they migrate to [TensorFlow Decision Forests](https://github.com/tensorflow/decision-forests), while guaranteeing that known vulnerabilities are fixed.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
These vulnerabilities have been reported by Yu Tian of Qihoo 360 AIVul Team and Faysal Hossain Shezan from University of Virginia. Some of the issues have been discovered internally after a careful audit of the APIs.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-57wx-m983-2f88
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h6gw-r52c-724r
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/e0b6e58c328059829c3eb968136f17aa72b6c876/tensorflow/core/kernels/boosted_trees/stats_ops.cc
