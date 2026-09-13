# [H] Netdata vulnerable to command injection

## Summary
Severity: High
Advisory: CVE-2023-22496
Aliases: GHSA-xg38-3vmw-2978
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-14
Source: https://osv.dev/vulnerability/CVE-2023-22496
Type: osv

## Details
Netdata is an open source option for real-time infrastructure monitoring and troubleshooting. An attacker with the ability to establish a streaming connection can execute arbitrary commands on the targeted Netdata agent. When an alert is triggered, the function `health_alarm_execute` is called. This function performs different checks and then enqueues a command by calling `spawn_enq_cmd`. This command is populated with several arguments that are not sanitized. One of them is the `registry_hostname` of the node for which the alert is raised. By providing a specially crafted `registry_hostname` as part of the health data that is streamed to a Netdata (parent) agent, an attacker can execute arbitrary commands at the remote host as a side-effect of the raised alert. Note that the commands are executed as the user running the Netdata Agent. This user is usually named `netdata`. The ability to run arbitrary commands may allow an attacker to escalate privileges by escalating other vulnerabilities in the system, as that user. The problem has been fixed in: Netdata agent v1.37 (stable) and Netdata agent v1.36.0-409 (nightly). As a workaround, streaming is not enabled by default. If you have previously enabled this, it can be disabled. Limiting access to the port on the recipient Agent to trusted child connections may mitigate the impact of this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22496.json
- https://github.com/netdata/netdata/security/advisories/GHSA-xg38-3vmw-2978
- https://nvd.nist.gov/vuln/detail/CVE-2023-22496
