# [M] Reporters can upload design to issues using the "Move to" feature

## Summary
Severity: Medium
Program: GitLab
Weakness: Privilege Escalation
Reporter: maruthi12
State: resolved
Disclosed: 2021-10-18T05:57:16.621Z
Source: https://hackerone.com/reports/1112297

## Details
### Summary

 According to the [permission documentation](https://docs.gitlab.com/ee/user/permissions.html), only role of `Developer` or more can upload  [Design Management](https://docs.gitlab.com/ee/user/project/issues/design_management.html) files. However, using the issue "Move to" feature, a reporter can create a issue with designs.

### Steps to reproduce

1. Consider a private project (say **Private Project**) with a member `Reporter`.
2. From Reporter's login, create a new project. (say **Reporter Project**).
3. Create an issue in *Reporter Project*.
4. Once the issue is created, upload a design to it.
5. Now, on the right hand panel bottom, click the *Move* button. 
6. Choose the *Private Project* as the destination project.
7. Now the issue along with the design are migrated to  the *Private Project*.

Let me know if you need anything else to reproduce this issue.

## Impact

Using the vulnerability, a Reporter can escalate his privilege to upload Design Management Files which he is not allowed to perform.
