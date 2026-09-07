# [H] Segfault in Tensorflow

## Summary
Severity: High
Advisory: GHSA-x7rp-74x2-mjf3
CVE: CVE-2020-15200
CWE: CWE-122, CWE-20, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-x7rp-74x2-mjf3
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The `RaggedCountSparseOutput` implementation does not validate that the input arguments form a valid ragged tensor. In particular, there is no validation that the values in the `splits` tensor generate a valid partitioning of the `values` tensor. Thus, the [following code](https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/count_ops.cc#L248-L265
) sets up conditions to cause a heap buffer overflow:
```cc
    auto per_batch_counts = BatchedMap<W>(num_batches);
    int batch_idx = 0;
    for (int idx = 0; idx < num_values; ++idx) {
      while (idx >= splits_values(batch_idx)) {
        batch_idx++;
      }
      const auto& value = values_values(idx);
      if (value >= 0 && (maxlength_ <= 0 || value < maxlength_)) {
        per_batch_counts[batch_idx - 1][value] = 1;
      }
    }
```

A `BatchedMap` is equivalent to a vector where each element is a hashmap. However, if the first element of `splits_values` is not 0, `batch_idx` will never be 1, hence there will be no hashmap at index 0 in `per_batch_counts`. Trying to access that in the user code results in a segmentation fault.

### Patches
We have patched the issue in 3cbb917b4714766030b28eba9fb41bb97ce9ee02 and will release a patch release.

We recommend users to upgrade to TensorFlow 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability is a variant of [GHSA-p5f8-gfw5-33w4](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p5f8-gfw5-33w4)

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x7rp-74x2-mjf3
- https://nvd.nist.gov/vuln/detail/CVE-2020-15200
- https://github.com/tensorflow/tensorflow/commit/3cbb917b4714766030b28eba9fb41bb97ce9ee02
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-280.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-315.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-123.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
