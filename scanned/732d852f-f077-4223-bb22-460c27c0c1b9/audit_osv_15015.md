# [H] CVE-2019-12995

## Summary
Severity: High
Advisory: CVE-2019-12995
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-28
Source: https://osv.dev/vulnerability/CVE-2019-12995
Type: osv

## Details
Istio before 1.2.2 mishandles certain access tokens, leading to "Epoch 0 terminated with an error" in Envoy. This is related to a jwt_authenticator.cc segmentation fault.

## References
- https://github.com/istio/istio.io/pull/4555
- https://github.com/istio/istio/issues/15084
- https://istio.io/about/notes/
