# [M] ALPINE-CVE-2023-0466

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-0466
Ecosystem: Alpine:v3.17
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-03-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0466
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.8-r3

## Details
The function X509_VERIFY_PARAM_add0_policy() is documented to
implicitly enable the certificate policy check when doing certificate
verification. However the implementation of the function does not
enable the check which allows certificates with invalid or incorrect
policies to pass the certificate verification.

As suddenly enabling the policy check could break existing deployments it was
decided to keep the existing behavior of the X509_VERIFY_PARAM_add0_policy()
function.

Instead the applications that require OpenSSL to perform certificate
policy check need to use X509_VERIFY_PARAM_set1_policies() or explicitly
enable the policy check by calling X509_VERIFY_PARAM_set_flags() with
the X509_V_FLAG_POLICY_CHECK flag argument.

Certificate policy checks are disabled by default in OpenSSL and are not
commonly used by applications.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0466
