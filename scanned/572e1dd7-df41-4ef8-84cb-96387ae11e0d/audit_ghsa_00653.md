# [M] Buffer not correctly recycled in Gzip Request inflation

## Summary
Severity: Medium
Advisory: GHSA-86wm-rrjm-8wh8
CVE: CVE-2020-27218
CWE: CWE-226
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2020-12-02
Source: https://github.com/advisories/GHSA-86wm-rrjm-8wh8
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.35.v20201120

## Details
### Impact
If GZIP request body inflation is enabled and requests from different clients are multiplexed onto a single connection and if an 
attacker can send a request with a body that is received entirely by not consumed by the application, then a subsequent request
on the same connection will see that body prepended to it's body.

The attacker will not see any data, but may inject data into the body of the subsequent request

CVE score is [4.8 AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L&version=3.1)

### Workarounds
The problem can be worked around by either:
- Disabling compressed request body inflation by GzipHandler.
- By always fully consuming the request content before sending a response.
- By adding a `Connection: close` to any response where the servlet does not fully consume request content.

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-86wm-rrjm-8wh8
- https://nvd.nist.gov/vuln/detail/CVE-2020-27218
- https://lists.apache.org/thread.html/rbbd003149f929b0e2fe58fb315de1658e98377225632e7e4239323fb@%3Ccommits.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbbd003149f929b0e2fe58fb315de1658e98377225632e7e4239323fb%40%3Ccommits.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rba4bca48d2cdfa8c08afc368a9cc4572ec85a5915ba29b8a194bf505@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rba4bca48d2cdfa8c08afc368a9cc4572ec85a5915ba29b8a194bf505%40%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rb8f413dc923070919b09db3ac87d079a2dcc6f0adfbb029e206a7930@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rb8f413dc923070919b09db3ac87d079a2dcc6f0adfbb029e206a7930%40%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rb6a3866c02ac4446451c7d9dceab2373b6d32fb058f9085c6143de30@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rb6a3866c02ac4446451c7d9dceab2373b6d32fb058f9085c6143de30%40%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/rb4ca79d1af5237108ce8770b7c46ca78095f62ef21331d9d06142388@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rb4ca79d1af5237108ce8770b7c46ca78095f62ef21331d9d06142388%40%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/racf9e6ad2482cb9b1e3e1b2c1b443d9d5cf14055fb54dec3d2dcce91@%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/racf9e6ad2482cb9b1e3e1b2c1b443d9d5cf14055fb54dec3d2dcce91%40%3Creviews.spark.apache.org%3E
- https://lists.apache.org/thread.html/racd55c9b704aa68cfb4436f17739b612b5d4f887155e04ed521a4b67@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/racd55c9b704aa68cfb4436f17739b612b5d4f887155e04ed521a4b67%40%3Cdev.kafka.apache.org%3E
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=568892
- https://lists.apache.org/thread.html/rbc5a8d7a0a13bc8152d427a7e9097cdeb139c6cfe111b2f00f26d16b%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbc5a8d7a0a13bc8152d427a7e9097cdeb139c6cfe111b2f00f26d16b@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbe3f2e0a3c38ed9cbef81507b7cc6e523341865e30dc15c7503adc76%40%3Cissues.spark.apache.org%3E
