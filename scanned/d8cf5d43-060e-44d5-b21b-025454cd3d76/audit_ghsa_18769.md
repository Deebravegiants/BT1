# [M] Keras is vulnerable to arbitrary local file loading and Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-mq84-hjqx-cwf2
CVE: CVE-2025-12058
CWE: CWE-502, CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:A/AC:H/AT:P/PR:L/UI:P/VC:H/VI:L/VA:L/SC:H/SI:L/SA:L/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-mq84-hjqx-cwf2
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.12.0

## Details
The Keras.Model.load_model method, including when executed with the intended security mitigation safe_mode=True, is vulnerable to arbitrary local file loading and Server-Side Request Forgery (SSRF).


This vulnerability stems from the way the StringLookup layer is handled during model loading from a specially crafted .keras archive. The constructor for the StringLookup layer accepts a vocabulary argument that can specify a local file path or a remote file path.

  *  Arbitrary Local File Read: An attacker can create a malicious .keras file that embeds a local path in the StringLookup layer's configuration. When the model is loaded, Keras will attempt to read the content of the specified local file and incorporate it into the model state (e.g., retrievable via get_vocabulary()), allowing an attacker to read arbitrary local files on the hosting system.


  *  Server-Side Request Forgery (SSRF): Keras utilizes tf.io.gfile for file operations. Since tf.io.gfile supports remote filesystem handlers (such as GCS and HDFS) and HTTP/HTTPS protocols, the same mechanism can be leveraged to fetch content from arbitrary network endpoints on the server's behalf, resulting in an SSRF condition.


The security issue is that the feature allowing external path loading was not properly restricted by the safe_mode=True flag, which was intended to prevent such unintended data access.

## References
- https://github.com/keras-team/keras/security/advisories/GHSA-qg93-c7p6-gg7f
- https://nvd.nist.gov/vuln/detail/CVE-2025-12058
- https://github.com/keras-team/keras/pull/21751
- https://github.com/keras-team/keras/commit/61ac8c1e51862c471dee7b49029c356f55531487
- https://github.com/keras-team/keras
- https://www.cve.org/CVERecord?id=CVE-2025-12058
