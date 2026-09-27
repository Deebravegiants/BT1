# [C] Fluentd is Vulnerable to Remote Code Execution (RCE) via Arbitrary File Write in `${tag}` Placeholder

## Summary
Severity: Critical
Advisory: GHSA-44hj-4m45-frj3
CVE: CVE-2026-44024
CWE: CWE-22, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-44hj-4m45-frj3
Type: github-advisory

## Affected
- RubyGems: `fluentd` — affected >=0 <1.19.3

## Details
Fluentd allows dynamically constructing file paths using the `${tag}` placeholder.
It was discovered that validation for this placeholder was insufficient.

If a Fluentd instance is configured to receive logs from untrusted sources and uses the `${tag}` placeholder in file configurations (such as the `path` parameter in the `out_file` plugin), an attacker can inject path traversal characters (e.g., `../`).

When combined with certain formatting options, this vulnerability allows an attacker to write arbitrary files or overwrite existing files on the system with attacker-controlled content, bypassing intended directory restrictions.

### Impact
This vulnerability allows for **Arbitrary File Write**, which can be directly escalated to full **Remote Code Execution (RCE)**.
An attacker could achieve RCE by overwriting critical system files, injecting executable plugins, or modifying configuration files.
The impact is Critical as it can lead to full system compromise without any authentication, depending on the Fluentd configuration and the privileges of the Fluentd process.

### Patches
v1.19.3

### Workarounds
If an immediate upgrade is not possible, users are strongly advised to apply the following mitigations:

1. Restrict Network Access
   * Ensure that Fluentd input ports (such as `in_forward` on default port `24224`) are deployed within a closed, trusted network. Use firewall rules (e.g., iptables, AWS Security Groups) to block access from untrusted networks or instances.
2. Run Fluentd as a non-root user
   * Dropping privileges prevents Fluentd from writing to sensitive system directories (e.g., `/etc/`), significantly mitigating the risk of system-wide RCE.
3. Revise configurations
   * Do not use the `${tag}` placeholder in the `path` parameter of output plugins (like `out_file`) if the tag originates from an untrusted source.
4. Filter incoming tags
   * Strictly validate and filter incoming tags at the input layer (e.g., using `fluent-plugin-rewrite-tag-filter`) to drop any tags containing `.` or `/` characters.

## References
- https://github.com/fluent/fluentd/security/advisories/GHSA-44hj-4m45-frj3
- https://github.com/fluent/fluentd
- https://github.com/fluent/fluentd/releases/tag/v1.19.3
