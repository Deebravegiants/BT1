# [M] Privilege escalation of "external user" (with maintainer privilege) to internal access  through project token

## Summary
Severity: Medium (CVSS 5.5)
Program: GitLab
Weakness: Privilege Escalation
Reporter: joaxcar
State: resolved
Disclosed: 2021-10-11T10:23:00.708Z
Source: https://hackerone.com/reports/1193062

## Details
### Summary

An "external user" (a user account with the status external) which is granted "Maintainer" role on any project on the GitLab instance where "project tokens" are allowed can elevate its privilege to "Internal". An external user with maintainer permissions could create a project token, which will be connected to a bot user with internal privileges on the GitLab instance. Thus, now being able to access all internal projects and snippets as a Guest user. This includes

* Accessing all information about internal projects as if having Guest permissions (including source code)
* Creating issues on internal projects
* Creating projects and groups (these will contain no members and thus be of little use)

An external user is by the documentation described as a way to let external contractors get access to limited parts of a GitLab instance [link](https://docs.gitlab.com/ee/user/permissions.html#external-users). Stating that
```
This feature may be useful when for example a contractor is working on a given project and should only have access to that project.
```
There are no warnings about giving an external user maintainer permissions. It is also possible for ANY internal user to elevate the external user to maintainer on any internal project created by that user. Thus, there is no need to ask an Admin for permission to do this. Thus, an external user (if not already granted maintainer on a project) only needs to convince one other user on the system to create a project and invite the external user as maintainer. 


### Steps to reproduce

1. Create a user with "external user" activated
2. Use any internal user to invite the "external user" as maintainer to a project
3. Login as the "external user" and create a project token on the project, save the token
4. Use the token to probe internal projects
```
 curl --header "Authorization: Bearer <TOKEN>" "https://gitlab.domain.com/api/v4/projects"
```
create groups
```
 curl -X POST --header "Authorization: Bearer <TOKEN>" "https://gitlab.domain.com/api/v4/groups?name=newg&path=newgroup"
```
create issues on internal projects
```
curl -X POST --header "Authorization: Bearer <TOKEN>" "https://gitlab.domain.com/api/v4/projects/21/issues?title=iWasHere" 
```
access source code
```
curl --header "Authorization: Bearer <TOKEN>" "https://gitlab.domain.com/api/v4/projects/19/repository/blobs/83d9398518bdf1519b7b8fbbb3fa3e305a8554ef/raw"
```

### Impact

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1193062_
