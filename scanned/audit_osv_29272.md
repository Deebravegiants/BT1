# [H] Monkeytype is vulnerable to Poisoned Pipeline Execution through Code Injection in its `ci-failure-comment.yml` GitHub Workflow, enabling attackers to gain `pull-requests` write access.

## Summary
Severity: High
Advisory: CVE-2024-41127
Aliases: GHSA-wcjf-5464-4wq9
CVSS: 8.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-08-02
Source: https://osv.dev/vulnerability/CVE-2024-41127
Type: osv

## Details
Monkeytype is a minimalistic and customizable typing test. Monkeytype is vulnerable to Poisoned Pipeline Execution through Code Injection in its ci-failure-comment.yml GitHub Workflow, enabling attackers to gain pull-requests write access. The ci-failure-comment.yml workflow is triggered when the Monkey CI workflow completes. When it runs, it will download an artifact uploaded by the triggering workflow and assign the contents of ./pr_num/pr_num.txt artifact to the steps.pr_num_reader.outputs.content WorkFlow variable. It is not validated that the variable is actually a number and later it is interpolated into a JS script allowing an attacker to change the code to be executed. This issue leads to pull-requests write access. This vulnerability is fixed in 24.30.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41127.json
- https://github.com/monkeytypegame/monkeytype/security/advisories/GHSA-wcjf-5464-4wq9
- https://nvd.nist.gov/vuln/detail/CVE-2024-41127
- https://securitylab.github.com/advisories/GHSL-2024-167_monkeytype
- https://github.com/monkeytypegame/monkeytype/commit/29627fd0d5f152e2da59671987090ea0a5c29874
