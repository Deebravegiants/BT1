# [H] Potential access control security issue in apollo-adminservice

## Summary
Severity: High
Advisory: GHSA-xpmx-h7xq-xffh
CVE: CVE-2020-15170
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2020-10-02
Source: https://github.com/advisories/GHSA-xpmx-h7xq-xffh
Type: github-advisory

## Affected
- Maven: `com.ctrip.framework.apollo:apollo-core` — affected >=0 <1.7.1

## Details
### Impact
If users expose apollo-adminservice to internet(which is not recommended), there are potential security issues since apollo-adminservice is designed to work in intranet and it doesn't have built-in access control. Malicious hackers may access apollo-adminservice apis directly to access/edit the application's configurations.

### Patches
Access control for admin service was added in #3233 and was released in [v1.7.1](https://github.com/ctripcorp/apollo/releases/tag/v1.7.1).

### Workarounds
To fix the potential issue without upgrading, simply follow the advice that do not expose apollo-adminservice to internet.

### Credits
[Lexu](https://github.com/lllllx) reported the issue and provided the required information to reproduce it.

### References
[Apollo Security Guidence](https://github.com/ctripcorp/apollo/wiki/Apollo%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97#71-%E5%AE%89%E5%85%A8%E7%9B%B8%E5%85%B3)

### For more information
If you have any questions or comments about this advisory:
* Open an [issue](https://github.com/ctripcorp/apollo/issues)
* Email to one of the active [project maintainers](https://github.com/ctripcorp/apollo/graphs/contributors)

## References
- https://github.com/ctripcorp/apollo/security/advisories/GHSA-xpmx-h7xq-xffh
- https://nvd.nist.gov/vuln/detail/CVE-2020-15170
- https://github.com/ctripcorp/apollo/pull/3233/commits/ae9ba6cfd32ed80469f162e5e3583e2477862ddf
- https://github.com/ctripcorp/apollo
