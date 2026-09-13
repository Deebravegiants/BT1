# [M] Crash in `tf.math.segment_*` operations

## Summary
Severity: Medium
Advisory: GHSA-cq76-mxrc-vchh
CVE: CVE-2021-41195
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-cq76-mxrc-vchh
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
The implementation of `tf.math.segment_*` operations results in a `CHECK`-fail related abort (and denial of service) if a segment id in `segment_ids` is large.

```python
import tensorflow as tf

tf.math.segment_max(data=np.ones((1,10,1)), segment_ids=[1676240524292489355])
tf.math.segment_min(data=np.ones((1,10,1)), segment_ids=[1676240524292489355])
tf.math.segment_mean(data=np.ones((1,10,1)), segment_ids=[1676240524292489355])    
tf.math.segment_sum(data=np.ones((1,10,1)), segment_ids=[1676240524292489355])
tf.math.segment_prod(data=np.ones((1,10,1)), segment_ids=[1676240524292489355])
```

This is similar to [CVE-2021-29584](https://github.com/tensorflow/tensorflow/blob/3a74f0307236fe206b046689c4d76f57c9b74eee/tensorflow/security/advisory/tfsa-2021-071.md) (and similar other reported vulnerabilities in TensorFlow, localized to specific APIs): the [implementation](https://github.com/tensorflow/tensorflow/blob/dae66e518c88de9c11718cd0f8f40a0b666a90a0/tensorflow/core/kernels/segment_reduction_ops_impl.h) (both on CPU and GPU) computes the output shape using [`AddDim`](https://github.com/tensorflow/tensorflow/blob/0b6b491d21d6a4eb5fbab1cca565bc1e94ca9543/tensorflow/core/framework/tensor_shape.cc#L395-L408). However, if the number of elements in the tensor overflows an `int64_t` value, `AddDim` results in a `CHECK` failure which provokes a `std::abort`. Instead, code should use [`AddDimWithStatus`](https://github.com/tensorflow/tensorflow/blob/0b6b491d21d6a4eb5fbab1cca565bc1e94ca9543/tensorflow/core/framework/tensor_shape.cc#L410-L440).


### Patches
We have patched the issue in GitHub commit [e9c81c1e1a9cd8dd31f4e83676cab61b60658429](https://github.com/tensorflow/tensorflow/commit/e9c81c1e1a9cd8dd31f4e83676cab61b60658429) (merging [#51733](https://github.com/tensorflow/tensorflow/pull/51733)).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.      

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.     

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/46888).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cq76-mxrc-vchh
- https://nvd.nist.gov/vuln/detail/CVE-2021-41195
- https://github.com/tensorflow/tensorflow/issues/46888
- https://github.com/tensorflow/tensorflow/pull/51733
- https://github.com/tensorflow/tensorflow/commit/e9c81c1e1a9cd8dd31f4e83676cab61b60658429
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-844.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-846.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-842.yaml
- https://github.com/tensorflow/tensorflow
