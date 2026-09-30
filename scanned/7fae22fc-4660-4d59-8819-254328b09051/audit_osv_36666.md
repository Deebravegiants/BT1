# [H] openITCOCKPIT has Unsafe PHP Deserialization in Gearman Worker Allowing Conditional Object Injection

## Summary
Severity: High
Advisory: CVE-2026-24891
Aliases: GHSA-x4mq-8gfg-frc4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-24891
Type: osv

## Details
openITCOCKPIT is an open source monitoring tool built for different monitoring engines like Nagios, Naemon and Prometheus. Versions 5.3.1 and below contain an unsafe deserialization sink in the Gearman worker implementation. The worker function registered as oitc_gearman calls PHP's unserialize() on job payloads without enforcing class restrictions or validating data origin. While the intended deployment assumes only trusted internal components enqueue Gearman jobs, this trust boundary is not enforced in application code. In environments where the Gearman service or worker is exposed to untrusted systems, an attacker may submit crafted serialized payloads to trigger PHP Object Injection in the worker process. This vulnerability is exploitable when Gearman listens on non-local interfaces, network access to TCP/4730 is unrestricted, or untrusted systems can enqueue jobs. Default, correctly hardened deployments may not be immediately exploitable, but the unsafe sink remains present in code regardless of deployment configuration. Enforcing this trust boundary in code would significantly reduce risk and prevent exploitation in misconfigured environments. This issue has been fixed in version 5.4.0.

## References
- https://github.com/openITCOCKPIT/openITCOCKPIT/releases/tag/openITCOCKPIT-5.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24891.json
- https://github.com/openITCOCKPIT/openITCOCKPIT/security/advisories/GHSA-x4mq-8gfg-frc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-24891
