# [M] CVE-2026-60065

## Summary
Severity: Medium
Advisory: CVE-2026-60065
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-60065
Type: osv

## Details
When NGINX Plus is configured to use the Message Queuing Telemetry Transport (MQTT) filter module (ngx_stream_mqtt_filter_module), unauthenticated attackers can send requests with conditions beyond the attacker's control to cause a heap buffer over-read in the NGINX worker process, leading to a restart.

Impact:
This vulnerability may allow remote unauthenticated attackers to have limited control to restart the NGINX worker process. There is no control plane exposure; this is a data plane issue only.

Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000162101
