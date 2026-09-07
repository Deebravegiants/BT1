# [M] Grafana Spoofing originalUrl of snapshots

## Summary
Severity: Medium
Advisory: GHSA-4724-7jwc-3fpw
CVE: CVE-2022-39324
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-4724-7jwc-3fpw
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.2.8
- Go: `github.com/grafana/grafana` — affected >=0 <8.5.16

## Details
To create a snapshot (and insert an arbitrary URL) the built-in role Viewer is sufficient.
When a dashboard is shared as a local snapshot, the following three fields are offered in the web UI for a user to fill out:
• Snapshotname
• Expire
• Timeout(seconds)
After the user confirms creation of the snapshot (i.e. clicks the ”Local Snapshot” button) an HTTP POST request is sent to the Grafana server. The HTTP request contains additional parameters that are not visible in the web UI. The parameter originalUrl is not visible in the web UI, but sent in the HTTP POST request.

The value of the originalUrl parameter is automatically generated. The purpose of the presented originalUrl parameter is to provide a user that views the snapshot the possibility to click on the button in the Grafana web UI and be presented with the dashboard that the snapshot was made out of.

The value of the originalUrl parameter can be arbitrarily chosen by a malicious user that creates the snapshot (Note: by editing the query thanks to a web proxy like Burp)
When another user opens the URL of the snapshot, they will be presented with the regular web interface delivered by the trusted Grafana server. The issue here is that the ”Open original dashboard” button no longer points to the to the real original dashboard but to the attacker’s (injected) URL.

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-4724-7jwc-3fpw
- https://nvd.nist.gov/vuln/detail/CVE-2022-39324
- https://github.com/grafana/grafana/pull/60232
- https://github.com/grafana/grafana/pull/60256
- https://github.com/grafana/grafana/commit/239888f22983010576bb3a9135a7294e88c0c74a
- https://github.com/grafana/grafana/commit/d7dcea71ea763780dc286792a0afd560bff2985c
- https://github.com/grafana/grafana
