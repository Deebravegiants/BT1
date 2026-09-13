# [H] Out of bounds write in TFLite

## Summary
Severity: High
Advisory: GHSA-9c78-vcq7-7vxq
CVE: CVE-2022-23561
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-9c78-vcq7-7vxq
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
An attacker can craft a TFLite model that would cause a write outside of bounds of an array in TFLite. In fact, the attacker can override the linked list used by the memory allocator. This can be leveraged for an arbitrary write primitive under certain conditions.

### Patches
We have patched the issue in GitHub commit [6c0b2b70eeee588591680f5b7d5d38175fd7cdf6](https://github.com/tensorflow/tensorflow/commit/6c0b2b70eeee588591680f5b7d5d38175fd7cdf6).
  
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.
    
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
  
### Attribution
This vulnerability has been reported by Wang Xuan of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9c78-vcq7-7vxq
- https://nvd.nist.gov/vuln/detail/CVE-2022-23561
- https://github.com/tensorflow/tensorflow/commit/6c0b2b70eeee588591680f5b7d5d38175fd7cdf6
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-70.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-125.yaml
- https://github.com/tensorflow/tensorflow
