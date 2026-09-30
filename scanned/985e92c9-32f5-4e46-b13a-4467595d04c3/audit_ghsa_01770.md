# [H] Insufficient Nonce Validation in Eclipse Milo Client

## Summary
Severity: High
Advisory: GHSA-pq4w-qm9g-qx68
CVE: CVE-2019-19135
CWE: CWE-330, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-03-16
Source: https://github.com/advisories/GHSA-pq4w-qm9g-qx68
Type: github-advisory

## Affected
- Maven: `org.eclipse.milo:sdk-client` — affected >=0 <0.3.6

## Details
### Impact
Credential replay affecting those connected to a server when *all 3* of the following conditions are met:
- `SecurityPolicy` is `None`
- using username/password or X509-based authentication
- the server has a defect causing it to send null/empty or zeroed nonces 

### Patches
The problem has been patched in version `0.3.6`. A more relaxed treatment of validation as agreed upon by the OPC UA Security Working Group is implemented in version `0.3.7`.

### Workarounds
Do not use username/password or X509-based authentication with `SecurityPolicy` of `None`.

### References
https://opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2019-19135.pdf

### For more information
If you have any questions or comments about this advisory:
* Open an issue at [https://github.com/eclipse/milo/issues](https://github.com/eclipse/milo/issues)
* Email [the mailing list](mailto:milo-dev@eclipse.org)

## References
- https://github.com/eclipse/milo/security/advisories/GHSA-pq4w-qm9g-qx68
- https://nvd.nist.gov/vuln/detail/CVE-2019-19135
- https://github.com/eclipse/milo/commit/cac0e710bf2b8bed9c602fc597e9de1d8903abed
- https://opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2019-19135.pdf
- https://opcfoundation.org/security-bulletins
