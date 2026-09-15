# [H] browserify-sign upper bound check issue in `dsaVerify` leads to a signature forgery attack

## Summary
Severity: High
Advisory: GHSA-x9w5-v3q2-3rhw
CVE: CVE-2023-46234
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-10-26
Source: https://github.com/advisories/GHSA-x9w5-v3q2-3rhw
Type: github-advisory

## Affected
- npm: `browserify-sign` — affected >=2.6.0 <4.2.2

## Details
### Summary
An upper bound check issue in `dsaVerify` function allows an attacker to construct signatures that can be successfully verified by any public key, thus leading to a signature forgery attack.

### Details
In `dsaVerify` function, it checks whether the value of the signature is legal by calling function `checkValue`, namely, whether `r` and `s` are both in the interval `[1, q - 1]`. However, the second line of the `checkValue` function wrongly checks the upper bound of the passed parameters, since the value of `b.cmp(q)` can only be `0`, `1` and `-1`, and it can never be greater than `q`. 

In this way, although the values of `s` cannot be `0`, an attacker can achieve the same effect as zero by setting its value to `q`, and then send `(r, s) = (1, q)` to pass the verification of any public key.

### Impact
All places in this project that involve DSA verification of user-input signatures will be affected by this vulnerability.


### Fix PR:
Since the temporary private fork was deleted, here's a webarchive of the PR discussion and diff pages: [PR webarchive.zip](https://github.com/browserify/browserify-sign/files/13172957/PR.webarchive.zip)

## References
- https://github.com/browserify/browserify-sign/security/advisories/GHSA-x9w5-v3q2-3rhw
- https://nvd.nist.gov/vuln/detail/CVE-2023-46234
- https://github.com/browserify/browserify-sign/commit/85994cd6348b50f2fd1b73c54e20881416f44a30
- https://github.com/browserify/browserify-sign
- https://lists.debian.org/debian-lts-announce/2023/10/msg00040.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3HUE6ZR5SL73KHL7XUPAOEL6SB7HUDT2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6PVVPNSAGSDS63HQ74PJ7MZ3MU5IYNVZ
- https://www.debian.org/security/2023/dsa-5539
