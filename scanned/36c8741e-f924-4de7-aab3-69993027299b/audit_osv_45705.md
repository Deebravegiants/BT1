# [M] The function `X509_VERIFY_PARAM_add0_policy()` is documented to implicitly enable the certificate...

## Summary
Severity: Medium
Advisory: JLSEC-2026-237
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-237
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.0.8+0 <3.0.9+0
- Julia: `Openresty_jll` — affected >=0 <1.27.1+0

## Details
The function `X509_VERIFY_PARAM_add0_policy()` is documented to
implicitly enable the certificate policy check when doing certificate
verification. However the implementation of the function does not
enable the check which allows certificates with invalid or incorrect
policies to pass the certificate verification.

As suddenly enabling the policy check could break existing deployments it was
decided to keep the existing behavior of the `X509_VERIFY_PARAM_add0_policy()`
function.

Instead the applications that require OpenSSL to perform certificate
policy check need to use `X509_VERIFY_PARAM_set1_policies()` or explicitly
enable the policy check by calling `X509_VERIFY_PARAM_set_flags()` with
the `X509_V_FLAG_POLICY_CHECK` flag argument.

Certificate policy checks are disabled by default in OpenSSL and are not
commonly used by applications.

## References
- http://www.openwall.com/lists/oss-security/2023/09/28/4
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=0d16b7e99aafc0b4a6d729eec65a411a7e025f0a
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=51e8a84ce742db0f6c70510d0159dad8f7825908
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=73398dea26de9899fb4baa94098ad0a61f435c72
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=fc814a30fc4f0bc54fcea7d9a7462f5457aab061
- https://github.com/advisories/GHSA-pxvj-4wx4-gv6w
- https://lists.debian.org/debian-lts-announce/2023/06/msg00011.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-0466
- https://security.gentoo.org/glsa/202402-08
- https://security.netapp.com/advisory/ntap-20230414-0001
- https://security.netapp.com/advisory/ntap-20230414-0001/
- https://www.debian.org/security/2023/dsa-5417
- https://www.openssl.org/news/secadv/20230328.txt
