# [M] DOS via move_issue

## Summary
Severity: Medium (CVSS 6.5)
Program: GitLab
Weakness: Uncontrolled Resource Consumption
Reporter: legit-security
State: resolved
Disclosed: 2022-11-04T03:44:34.198Z
Source: https://hackerone.com/reports/1543584

## Details
### Summary
Moving an issue with a specially-crafted description results in high CPU usage for 60 seconds (request timeout).
Multiple requests can be issued in parallel to create a larger impact.

### Steps to reproduce
1. Given an authorized user (on GitLab.com - anyone can self-register. On EE - depends on instance configuration).
2. Create an issue with the following description (provided a one-line python script to avoid bloating):
3. Once created, move the issue to a different project.

The script:
```python -c "print('![l' * 100000 + '\n')"```
Note: works with a lower number of repetitions too.


### Impact
After 60 seconds (timeout) - the request fails.
Meanwhile, on the server end, (a single) CPU is burnt out (verified against a local EE instance).
Issuing multiple requests in parallel (on multiple GitLab issues) results in multiple CPUs burn out.
Using the DockerHub image, the entire server is completely unavailable by repeatedly sending a small number of requests repeatedly.

### Examples
The bug is instance-independent, works on latest versions. Since GitLab.com is open-core - it would work on GitLab too.

### What is the current *bug* behavior?
The HTTP request fails for timeout while the server is burning CPU.

On the code side:
lib/gitlab/gfm/uploads_rewriter.rb / module Gitlab/Gfm / class UploadsRewriter / function files:
```@text.scan(@pattern)```
Where FileUploader::MARKDOWN_PATTERN is assigned to the pattern data member.

MARKDOWN_PATTERN is: 
```\!?\[.*?\]\(/uploads/(?<secret>[0-9a-f]{32})/(?<file>.*?)\)```
The pattern is of a polynomial complexity, thus, the scan results in high CPU utilization.

### What is the expected *correct* behavior?
Instead of using Ruby’s default Regex engine, use the RE2 engine (or the wrapped version at lib/gitlab/untrusted_regexp.rb), with the following pattern:
```\!?\[.*\]\(/uploads/([0-9a-f]{32})/(.*)\)```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1543584_
