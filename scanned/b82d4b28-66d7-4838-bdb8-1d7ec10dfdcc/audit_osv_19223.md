# [H] CVE-2020-8843

## Summary
Severity: High
Advisory: CVE-2020-8843
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-02-14
Source: https://osv.dev/vulnerability/CVE-2020-8843
Type: osv

## Details
An issue was discovered in Istio 1.3 through 1.3.6. Under certain circumstances, it is possible to bypass a specifically configured Mixer policy. Istio-proxy accepts the x-istio-attributes header at ingress that can be used to affect policy decisions when Mixer policy selectively applies to a source equal to ingress. To exploit this vulnerability, someone has to encode a source.uid in this header. This feature is disabled by default in Istio 1.3 and 1.4.

## References
- https://istio.io/news/security/
- https://istio.io/news/security/istio-security-2020-002/
- https://github.com/istio/istio/commits/master
