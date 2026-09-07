# [M] Crash caused by integer conversion to unsigned

## Summary
Severity: Medium
Advisory: GHSA-gf88-j2mg-cc82
CVE: CVE-2021-37661
CWE: CWE-681
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gf88-j2mg-cc82
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
An attacker can cause a denial of service in `boosted_trees_create_quantile_stream_resource` by using negative arguments:

```python
import tensorflow as tf
from tensorflow.python.ops import gen_boosted_trees_ops
import numpy as np

v= tf.Variable([0.0, 0.0, 0.0, 0.0, 0.0])
gen_boosted_trees_ops.boosted_trees_create_quantile_stream_resource(
  quantile_stream_resource_handle = v.handle,
  epsilon = [74.82224],
  num_streams = [-49], 
  max_elements = np.int32(586))
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/84d053187cb80d975ef2b9684d4b61981bca0c41/tensorflow/core/kernels/boosted_trees/quantile_ops.cc#L96) does not validate that `num_streams` only contains non-negative numbers. In turn, [this results in using this value to allocate memory](https://github.com/tensorflow/tensorflow/blob/84d053187cb80d975ef2b9684d4b61981bca0c41/tensorflow/core/kernels/boosted_trees/quantiles/quantile_stream_resource.h#L31-L40):

```cc
class BoostedTreesQuantileStreamResource : public ResourceBase {
 public:
  BoostedTreesQuantileStreamResource(const float epsilon,
                                     const int64 max_elements,
                                     const int64 num_streams)
      : are_buckets_ready_(false),
        epsilon_(epsilon),
        num_streams_(num_streams),
        max_elements_(max_elements) {
    streams_.reserve(num_streams_);
    ...
  }
}
```

However, `reserve` receives an unsigned integer so there is an implicit conversion from a negative value to a large positive unsigned. This results in a crash from the standard library.

### Patches
We have patched the issue in GitHub commit [8a84f7a2b5a2b27ecf88d25bad9ac777cd2f7992](https://github.com/tensorflow/tensorflow/commit/8a84f7a2b5a2b27ecf88d25bad9ac777cd2f7992).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gf88-j2mg-cc82
- https://nvd.nist.gov/vuln/detail/CVE-2021-37661
- https://github.com/tensorflow/tensorflow/commit/8a84f7a2b5a2b27ecf88d25bad9ac777cd2f7992
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-574.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-772.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-283.yaml
- https://github.com/tensorflow/tensorflow
