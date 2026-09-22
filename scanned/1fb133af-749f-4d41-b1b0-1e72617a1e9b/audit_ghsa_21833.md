# [H] Out of bounds write in Tensorflow

## Summary
Severity: High
Advisory: GHSA-5qw5-89mw-wcg2
CVE: CVE-2022-23566
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-5qw5-89mw-wcg2
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
TensorFlow is vulnerable to a heap OOB write in [Grappler](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/costs/graph_properties.cc#L1132-L1141):

```cc
Status SetUnknownShape(const NodeDef* node, int output_port) {
  shape_inference::ShapeHandle shape = 
      GetUnknownOutputShape(node, output_port);
  InferenceContext* ctx = GetContext(node);
  if (ctx == nullptr) {
    return errors::InvalidArgument("Missing context");
  }
  ctx->set_output(output_port, shape);
  return Status::OK();
}
```

The [`set_output`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/framework/shape_inference.h#L394) function writes to an array at the specified index:

```cc
void set_output(int idx, ShapeHandle shape) { outputs_.at(idx) = shape; }
```

Hence, this gives a malicious user a write primitive.

### Patches
We have patched the issue in GitHub commit [97282c6d0d34476b6ba033f961590b783fa184cd](https://github.com/tensorflow/tensorflow/commit/97282c6d0d34476b6ba033f961590b783fa184cd).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5qw5-89mw-wcg2
- https://nvd.nist.gov/vuln/detail/CVE-2022-23566
- https://github.com/tensorflow/tensorflow/commit/97282c6d0d34476b6ba033f961590b783fa184cd
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-75.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-130.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/framework/shape_inference.h#L394
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/costs/graph_properties.cc#L1132-L1141
