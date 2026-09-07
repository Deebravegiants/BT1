# [H] Zendframework Denial of Service vector via XEE injection

## Summary
Severity: High
Advisory: GHSA-2jx7-xg83-j2m7
CWE: CWE-776
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-2jx7-xg83-j2m7
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.0.0 <1.11.13

## Details
`Zend_Dom`, `Zend_Feed`, `Zend_Soap`, and `Zend_XmlRpc` are vulnerable to XML Entity Expansion (XEE) vectors, leading to Denial of Service vectors. XEE attacks occur when the XML DOCTYPE declaration includes XML entity definitions that contain either recursive or circular references; this leads to CPU and memory consumption, making Denial of Service exploits trivial to implement.

## References
- https://framework.zend.com/security/advisory/ZF2012-02
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2012-02.yaml
- https://github.com/zendframework/zf1
