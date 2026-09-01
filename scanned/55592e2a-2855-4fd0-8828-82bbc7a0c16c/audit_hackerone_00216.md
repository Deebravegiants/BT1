# [M] SSRF into Shared Runner, by replacing dockerd with malicious server in Executor

## Summary
Severity: Medium
Program: GitLab
Weakness: Server-Side Request Forgery (SSRF)
Reporter: lucash-dev
State: resolved
Disclosed: 2020-09-08T13:28:39.515Z
Source: https://hackerone.com/reports/809248

## Details
# Note

I've assigned the severity HIGH and submitted this report based on previously disclosed blind SSRF bugs that were previously disclosed.
(https://hackerone.com/reports/398799)
If that's not correct, please adjust or let me know if you require more immediate impact on users in order to consider it.


# Description

The Shared Runners implementation has a bug in its docker client
that allows following HTTP redirection. Because it accesses the
docker daemons running in executors -- which are completely under
control of users -- a malicious user can replace the existing
dockerd with a malicious HTTPS server that sends redirect responses.
The TLS validation can't prevent this attack, as both public and
private keys used by the docker daemon in the executor are also
under the CI job's (so the user's) control.

An attacker can use that to perform (mostly blind) SSRF attacks
targetting the Shared Runner local host, link-local and local networks.
In case of an error response from the target, the response body
will be displayed in the CI job's logs.
A succcessful HTTP request will result in the first character of
the response being visible, or -- if the response is a valid JSON --
will cause the process to hang.
TCP (other than HTTP) targets also partially reveal the response.

This can be used, for example to send requests to Google Cloud's metadata
service, but so far I've been unable to obtain the access token
(only the first character `a` is visible).

The culprit seems to be 
`https://gitlab.com/gitlab-org/gitlab-runner/-/blob/master/helpers/docker/official_docker_client.go#L45`

The line `httpClient := &http.Client{Transport: transport}` seems to be missing a proper
redirect policy.



_Trimmed to 38 lines — full report: https://hackerone.com/reports/809248_
