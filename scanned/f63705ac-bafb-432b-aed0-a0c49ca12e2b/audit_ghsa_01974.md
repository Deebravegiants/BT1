# [M] Action Commands (run/shell/exec) Against Library URIs Ignore Configured Remote Endpoint

## Summary
Severity: Medium
Advisory: GHSA-jq42-hfch-42f3
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-06-01
Source: https://github.com/advisories/GHSA-jq42-hfch-42f3
Type: github-advisory

## Affected
- Go: `github.com/hpcng/singularity` — affected >=3.7.2 <3.7.4

## Details
# Impact
Due to incorrect use of a default URL, `singularity` action commands (`run`/`shell`/`exec`) specifying a container using a `library://` URI will always attempt to retrieve the container from the default remote endpoint (`cloud.sylabs.io`) rather than the configured remote endpoint.

An attacker may be able to push a malicious container to the default remote endpoint with a URI that is identical to the URI used by a victim with a non-default remote endpoint, thus executing the malicious container.

Only action commands (`run`/`shell`/`exec`) against `library://` URIs are affected. Other commands such as `pull` / `push` respect the configured remote endpoint.

# Patches
All users should upgrade to Singularity 3.7.4 or later.

# Workarounds
Users who only interact with the default remote endpoint or do not use the library:// url are not affected.

Installations with an execution control list configured to restrict execution to containers signed with specific secure keys are not affected.

# Acknowledgements
This issue was found by Mike Frisch and brought to our attention by Sylabs.  Sylabs is making a [coordinated disclosure](https://github.com/sylabs/singularity/security/advisories/GHSA-5mv9-q7fq-9394).

# For more information
General questions about the impact of the advisory can be asked in the:

[Singularity Slack Channel](https://join.slack.com/t/hpcng/shared_invite/zt-qda4h1ls-OP0Uouq6sSmVE6i_0NrWdw)
[Singularity Mailing List](https://groups.google.com/a/lbl.gov/g/singularity)
Any sensitive security concerns should be directed to: [singularity-security@hpcng.org](mailto:singularity-security@hpcng.org)

## References
- https://github.com/hpcng/singularity/security/advisories/GHSA-jq42-hfch-42f3
- https://github.com/sylabs/singularity/security/advisories/GHSA-5mv9-q7fq-9394
- https://github.com/hpcng/singularity
