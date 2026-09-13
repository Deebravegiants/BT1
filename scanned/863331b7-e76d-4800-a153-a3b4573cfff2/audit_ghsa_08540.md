# [H] Calico Inserts Sensitive Information into Log File

## Summary
Severity: High
Advisory: GHSA-3m4q-ggcj-j6m4
CVE: CVE-2026-6720
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-3m4q-ggcj-j6m4
Type: github-advisory

## Affected
- Go: `github.com/projectcalico/calicoctl/v3` — affected >=0 <3.31.6

## Details
When calicoctl is invoked with --log-level=info or --log-level=debug, the client prints the full contents of its loaded connection-configuration struct to stderr in a single log line. The struct embeds every credential calicoctl uses to talk to the cluster — inline kubeconfig (with bearer token), Kubernetes API bearer token, etcd password, and inline PEM-encoded etcd client certificate and key. Any reader of that stderr stream — CI job logs, session-recording archives, shared support-ticket transcripts, or local filesystem viewers on the host that ran calicoctl — can extract these credentials with zero Kubernetes privilege. calicoctl's default log level is panic, so this issue only triggers when verbose logging is explicitly enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6720
- https://github.com/projectcalico/calico/pull/12535
- https://github.com/projectcalico/calico/pull/12536
- https://github.com/projectcalico/calico/pull/12537
- https://github.com/projectcalico/calico/commit/12908bb48a5bf8cbab5373f4d532509a30cf9b7f
- https://github.com/projectcalico/calico/commit/8d87eddcb5eb6efc70c09eb0a33d63137359ea70
- https://github.com/projectcalico/calico/commit/ce3ab2b39b5841757cbccf7922c895c47827f562
- https://github.com/projectcalico/calico
- https://www.tigera.io/security-bulletins/tta-2026-003
