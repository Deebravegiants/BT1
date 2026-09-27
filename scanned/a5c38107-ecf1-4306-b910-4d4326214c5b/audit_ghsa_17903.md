# [M] NeuVector process with sensitive arguments lead to leakage

## Summary
Severity: Medium
Advisory: GHSA-w54x-xfxg-4gxq
CVE: CVE-2025-54467
CWE: CWE-522, CWE-549
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-w54x-xfxg-4gxq
Type: github-advisory

## Affected
- Go: `github.com/neuvector/neuvector` — affected >=0 <0.0.0-20250902144615-f9ddbdf42031

## Details
### Impact

When a Java command with password parameters is executed and terminated by NeuVector for Process rule violation. For example, 

```
java -cp /app ... Djavax.net.ssl.trustStorePassword=<Password>
```

The command with the password appears in the NeuVector security event. To prevent this, NeuVector uses the following default regular expression to detect and redact sensitive data from process commands:

```
(?i)(password|passwd|token)
```

Also, you can define custom patterns to redact by creating a Kubernetes ConfigMap. For example:

```
kubectl create configmap neuvector-custom-rules --from-file=secret-patterns.yaml -n neuvector
```

Sample `secret-patterns.yaml` content:

```
Pattern_list:
  - (?i)(pawd|pword)
  - (?i)(secret)
```

NeuVector uses the default and custom regex to decide whether the process command in a security event should be redacted.

**Note:** If numerous regular expression (regex) patterns are configured in the Kubernetes ConfigMap for extended coverage of sensitive data matching, it can significantly impact performance of NeuVector enforcer, particularly in scenarios involving large inputs or frequent execution. The primary factor contributing to performance issues in regex is backtracking, where the regex engine attempts various matching paths when a pattern doesn't immediately find a match.

### Patches

This issue is fixed in NeuVector version **5.4.6** and later.

### Workarounds

There is no workaround. Upgrade to a patched version of NeuVector as soon as possible.

### References

If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [NeuVector](https://github.com/neuvector/neuvector/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-neuvector/support-matrix/all-supported-versions/neuvector-v-all-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/#suse-security).

## References
- https://github.com/neuvector/neuvector/security/advisories/GHSA-w54x-xfxg-4gxq
- https://nvd.nist.gov/vuln/detail/CVE-2025-54467
- https://github.com/neuvector/neuvector/commit/f9ddbdf420319cede3c490c1de03f48d953896ae
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-54467
- https://github.com/neuvector/neuvector
