# [H] Nomad Job Submitter Privilege Escalation Using Workload Identity

## Summary
Severity: High
Advisory: GHSA-rqm8-q8j9-662f
CVE: CVE-2023-1299
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-14
Source: https://github.com/advisories/GHSA-rqm8-q8j9-662f
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=1.5.0 <1.5.1

## Details
### Summary
A vulnerability was identified in Nomad and Nomad Enterprise (“Nomad”) such that a user with the submit-job ACL capability can submit a job that can escalate to management-level privileges. This vulnerability, CVE-2023-1299, was introduced in Nomad 1.5.0 and fixed in Nomad 1.5.1.

### Background
Nomad 1.4.0 introduced the concept of workload identity so that tasks can access variables without needing to access them through Nomad HTTP API with an ACL token.

In 1.5.0, the identity block was introduced, which exposes the workload identity token to the workload so it can access Nomad HTTP API via a unix domain socket without configuring mTLS.

### Details
During internal testing, we discovered it was possible to abuse the workload identity to elevate to management-level privilege if the workload identity did not have any attached ACL policies.

### Remediation
Customers should evaluate the risk associated with this issue and consider upgrading to Nomad 1.5.1 or newer. See Nomad’s Upgrading for general guidance on this process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1299
- https://discuss.hashicorp.com/t/hcsec-2023-08-nomad-job-submitter-privilege-escalation-using-workload-identity/51389
- https://github.com/hashicorp/nomad
