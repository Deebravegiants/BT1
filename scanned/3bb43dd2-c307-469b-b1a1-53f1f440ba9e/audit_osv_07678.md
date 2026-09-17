# [C] BIT-tensorflow-2021-35958

## Summary
Severity: Critical
Advisory: BIT-tensorflow-2021-35958
Aliases: CVE-2021-35958
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-35958
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=0 <2.5.1

## Details
TensorFlow through 2.5.0 allows attackers to overwrite arbitrary files via a crafted archive when tf.keras.utils.get_file is used with extract=True. NOTE: the vendor's position is that tf.keras.utils.get_file is not intended for untrusted archives

## References
- https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractall
- https://github.com/tensorflow/tensorflow/blob/b8cad4c631096a34461ff8a07840d5f4d123ce32/tensorflow/python/keras/README.md
- https://github.com/tensorflow/tensorflow/blob/b8cad4c631096a34461ff8a07840d5f4d123ce32/tensorflow/python/keras/utils/data_utils.py#L137
- https://keras.io/api/
- https://vuln.ryotak.me/advisories/52
- https://nvd.nist.gov/vuln/detail/CVE-2021-35958
