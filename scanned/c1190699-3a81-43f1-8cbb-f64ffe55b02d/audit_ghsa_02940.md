# [H] Use after free / memory leak in `CollectiveReduceV2`

## Summary
Severity: High
Advisory: GHSA-gpfh-jvf9-7wg5
CVE: CVE-2021-41220
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-gpfh-jvf9-7wg5
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1

## Details
### Impact
The [async implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/collective_ops.cc#L604-L615) of `CollectiveReduceV2` suffers from a memory leak and a use after free:

```python
import tensorflow as tf
  
tf.raw_ops.CollectiveReduceV2(
  input=[],
  group_size=[-10, -10, -10],
  group_key=[-10, -10],
  instance_key=[-10],
  ordering_token=[],
  merge_op='Mul',
  final_op='Div')
``` 

This occurs due to the asynchronous computation and the fact that objects that have been `std::move()`d from are still accessed:

```cc
auto done_with_cleanup = [col_params, done = std::move(done)]() {
  done();
  col_params->Unref();
};
OP_REQUIRES_OK_ASYNC(c,
                     FillCollectiveParams(col_params, REDUCTION_COLLECTIVE,
                                          /*group_size*/ c->input(1),
                                          /*group_key*/ c->input(2),
                                          /*instance_key*/ c->input(3)),
                     done);
```

Here, `done` is already moved from by the time `OP_REQUIRES_OK_ASYNC` macro needs to invoke it in case of errors. In this case, we get an undefined behavior, which can manifest via crashes, `std::bad_alloc` throws or just memory leaks.

### Patches
We have patched the issue in GitHub commit [ca38dab9d3ee66c5de06f11af9a4b1200da5ef75](https://github.com/tensorflow/tensorflow/commit/ca38dab9d3ee66c5de06f11af9a4b1200da5ef75).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, as this version is the only one that is also affected.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gpfh-jvf9-7wg5
- https://nvd.nist.gov/vuln/detail/CVE-2021-41220
- https://github.com/tensorflow/tensorflow/commit/ca38dab9d3ee66c5de06f11af9a4b1200da5ef75
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-629.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-827.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-412.yaml
- https://github.com/tensorflow/tensorflow
