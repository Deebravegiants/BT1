# [H] HTTP/2: CPU exhaustion due to CONTINUATION frame flood

## Summary
Severity: High
Advisory: BIT-envoy-2024-30255
Aliases: CVE-2024-30255, GHSA-j654-3ccm-vfmm
Ecosystem: Bitnami
Published: 2024-04-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-30255
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.29.0 <1.29.3

## Details
Envoy is a cloud-native, open source edge and service proxy. The HTTP/2 protocol stack in Envoy versions prior to 1.29.3, 1.28.2, 1.27.4, and 1.26.8 are vulnerable to CPU exhaustion due to flood of CONTINUATION frames. Envoy's HTTP/2 codec allows the client to send an unlimited number of CONTINUATION frames even after exceeding Envoy's header map limits. This allows an attacker to send a sequence of CONTINUATION frames without the END_HEADERS bit set causing CPU utilization, consuming approximately 1 core per 300Mbit/s of traffic and culminating in denial of service through CPU exhaustion. Users should upgrade to version 1.29.3, 1.28.2, 1.27.4, or 1.26.8 to mitigate the effects of the CONTINUATION flood. As a workaround, disable HTTP/2 protocol for downstream connections.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-j654-3ccm-vfmm
- http://www.openwall.com/lists/oss-security/2024/04/03/16
- http://www.openwall.com/lists/oss-security/2024/04/05/3
- https://nvd.nist.gov/vuln/detail/CVE-2024-30255
- https://www.kb.cert.org/vuls/id/421644
