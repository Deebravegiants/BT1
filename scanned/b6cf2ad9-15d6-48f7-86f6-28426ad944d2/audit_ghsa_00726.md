# [H] Denial of Service in Cryptacular

## Summary
Severity: High
Advisory: GHSA-x64g-4xx9-fh6x
CVE: CVE-2020-7226
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-x64g-4xx9-fh6x
Type: github-advisory

## Affected
- Maven: `org.cryptacular:cryptacular` — affected >=0 <1.1.4
- Maven: `org.cryptacular:cryptacular` — affected >=1.2.0 <1.2.4

## Details
CiphertextHeader.java in Cryptacular before 1.2.4, as used in Apereo CAS and other products, allows attackers to trigger excessive memory allocation during a decode operation, because the nonce array length associated with &quot;new byte&quot; may depend on untrusted input within the header of encoded data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7226
- https://github.com/vt-middleware/cryptacular/issues/52
- https://github.com/apereo/cas/pull/4685
- https://github.com/vt-middleware/cryptacular/pull/56
- https://github.com/apereo/cas/commit/8810f2b6c71d73341d4dde6b09a18eb46cfd6d45
- https://github.com/apereo/cas/commit/93b1c3e9d90e36a19d0fa0f6efb863c6f0235e75
- https://github.com/apereo/cas/commit/a042808d6adbbf44753d52c55cac5f533e24101f
- https://github.com/vt-middleware/cryptacular/commit/311baf12252abf21947afd07bf0a0291ec3ec796
- https://github.com/vt-middleware/cryptacular/commit/ec2fb65f2455c479376695e3d75d30c7f6884b3f
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://lists.apache.org/thread.html/rfa4647c58e375996e62a9094bffff6dc350ec311ba955b430e738945@%3Cdev.ws.apache.org%3E
- https://lists.apache.org/thread.html/re7f46c4cc29a4616e0aa669c84a0eb34832e83a8eef05189e2e59b44@%3Cdev.ws.apache.org%3E
- https://lists.apache.org/thread.html/re04e4f8f0d095387fb6b0ff9016a0af8c93f42e1de93b09298bfa547@%3Ccommits.ws.apache.org%3E
- https://lists.apache.org/thread.html/rc36b75cabb4d700b48035d15ad8b8c2712bb32123572a1bdaec2510a@%3Cdev.ws.apache.org%3E
- https://lists.apache.org/thread.html/r77c48cd851f60833df9a9c9c31f12243508e15d1b2a0961066d44fc6@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r4a62133ad01d5f963755021027a4cce23f76b8674a13860d2978c7c8@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r380781f5b489cb3c818536cd3b3757e806bfe0bca188591e0051ac03@%3Ccommits.ws.apache.org%3E
- https://lists.apache.org/thread.html/r2237a27040b57adc2fcc5570bd530ad2038e67fcb2a3ce65283d3143@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r209de85beae4d257d27fc577e3a3e97039bdb4c2dc6f4a8e5a5a5811@%3Ccommits.tomee.apache.org%3E
