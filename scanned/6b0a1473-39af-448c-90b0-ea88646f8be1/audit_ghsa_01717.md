# [M] IDOR can reveal execution data and logs to unauthorized user in Rundeck

## Summary
Severity: Medium
Advisory: GHSA-5679-7qrc-5m7j
CVE: CVE-2020-11009
CWE: CWE-200, CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-04-29
Source: https://github.com/advisories/GHSA-5679-7qrc-5m7j
Type: github-advisory

## Affected
- Maven: `org.rundeck:rundeck` — affected >=0 <3.2.6

## Details
### Impact

Authenticated users can craft a request that reveals Execution data and logs  and Job details that they are not authorized to see.

> Depending on the configuration and the way that Rundeck is used, this could result in anything between a high severity risk, or a very low risk. If access is tightly restricted and all users on the system have access to all projects, this is not really much of an issue. If access is wider and allows login for users that do not have access to any projects, or project access is restricted, there is a larger issue. If access is meant to be restricted and secrets, sensitive data, or intellectual property are exposed in Rundeck execution output and job data, the risk becomes much higher.

### Details

An authenticated user could craft a request to:

* View Executions and download execution logs without access to `read` or `view` the associated Job, or ad-hoc resource.
* Get the list of running executions in a project, without Event `read` access, if they have `read` access to view the project.
* View the Options definitions of a Job without access to view the Job.
* View the definition of a workflow step of a Job without access to view the Job.
* View the SCM diff of a modified Job definition if SCM is enabled, without Project `export` access level.
* View the New User Profile Form for a different username, without User `admin` access. Note: they would not be allowed to create or modify a profile for a different user, or reveal any user profile information for a different user.

Some authenticated API requests were not correctly checking appropriate authorization levels:

* The list of running Executions would be sent without `read` access to Events.
* The Plugin Input Parameters for a SCM plugin would be sent without authorization for project `import`,`scm_import`,`export`, or `scm_export` actions.
* Job Retry action could retry an execution without `read` or `view` access to the Execution, which would reveal the Execution's option values. (`run` access to the Job was still required).

### Patches
Upgrade to Rundeck version 3.2.6

### Workarounds
None

### References
[3.2.6 Release Notes](https://docs.rundeck.com/docs/history/3_2_x/version-3.2.6.html)

### Report
If you have any questions or comments about this advisory:
* Email us at [security@rundeck.com](mailto:security@rundeck.com)

To report security issues to Rundeck please use the form at [http://rundeck.com/security](http://rundeck.com/security)

Reporter: Justine Osborne of Apple Information Security

## References
- https://github.com/rundeck/rundeck/security/advisories/GHSA-5679-7qrc-5m7j
- https://nvd.nist.gov/vuln/detail/CVE-2020-11009
- https://docs.rundeck.com/docs/history/3_2_x/version-3.2.6.html
- https://github.com/rundeck/rundeck
