# [C] SSRF into Sandbox Escape through Unsafe Default Configuration

## Summary
Severity: Critical
Advisory: CVE-2024-29021
Aliases: GHSA-q7vg-26pg-v5hr
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-04-18
Source: https://osv.dev/vulnerability/CVE-2024-29021
Type: osv

## Details
Judge0 is an open-source online code execution system. The default configuration of Judge0 leaves the service vulnerable to a sandbox escape via Server Side Request Forgery (SSRF). This allows an attacker with sufficient access to the Judge0 API to obtain unsandboxed code execution as root on the target machine. This vulnerability is fixed in 1.13.1.

## References
- https://github.com/judge0/judge0/blob/ad66f77b131dbbebf2b9ff8083dca9a68680b3e5/app/jobs/isolate_job.rb#L203-L230
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29021.json
- https://github.com/judge0/judge0/security/advisories/GHSA-q7vg-26pg-v5hr
- https://nvd.nist.gov/vuln/detail/CVE-2024-29021
