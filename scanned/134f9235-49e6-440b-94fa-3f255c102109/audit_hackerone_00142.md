# [M] A deactivated user can access data through GraphQL

## Summary
Severity: Medium
Program: GitLab
Weakness: Improper Access Control - Generic
Reporter: joaxcar
State: resolved
Disclosed: 2021-08-30T13:25:12.844Z
Source: https://hackerone.com/reports/1192460

## Details
### Summary

A deactivated user should not be able to access information through the API. This rule is not enforced when making requests through the GraphQL endpoint. 

When reading through the changelog for 13.11.2 i noticed that the rule for a deactivated user allows for :log_in (as it should) but it is restricted from :access_api(as it should) [link](https://gitlab.com/gitlab-org/gitlab/-/blob/e568b72493328ad271ddb38f0b22109bc91d8447/app/policies/global_policy.rb#L64). The GraphQL endpoint does not seam to use this rules when authorizing a user. I guess GraphQL only checks for api scope on the user.

This opens for three potential problems:

* A user using its account through the GraphQL API (through some script or similar) would not get a warning that the account is deactivated. This could lead to the account being removed if the entities controlling the GitLab instance has any automatic procedures deleting accounts. When reading about the deactivation feature I got the impression that most admins requesting the feature would use it in automated "cleanings" of their user base. I could see how an admin could implement a "deactivate after 90 days inactivity" and "delete after 180 days inactivity" rule or similar. This could lead to an account being "in use" through GraphQL could get deleted without proper warnings.
* An admin could use deactivated accounts as "bots" or "service accounts" bypassing the billing of these accounts. (an admin can create users and deactivate them directly, before ever using the account)
* The fact that the account should not be able to do this. An admin reading the docs are under the assumption that a deactivated account is blocked from using the API. An inactive user could have left some form of scripts running that would keep on using resources on the GitLab instance, which I guess the admin would like to remediate by deactivating the account.

__as of 13.10.4:__ A deactivated user can (without activating its account) use read queries on the GraphQL endpoint. The latest security patch removes the ability to use mutations due to the fact that 
 ```
   rule { deactivated }.policy do
    prevent :access_git
    prevent :access_api
    prevent :receive_notifications
    prevent :use_slash_commands
  end
```
prevents :access_api, and
```
rule { ~can?(:access_api) }.prevent :execute_graphql_mutation
```
prevents from using mutations if I understand the code correctly.

__tested on 13.11.1:__  (Prior to latest security patch 13.11.2) A deactivated user can (without activating its account) use queries and mutations on the GraphQL endpoint.

### Steps to reproduce

__Unlimited service accounts__
1. Login as admin
2. Create a user
3. Deactivate the user
4. Create an api token for the deactivated user
5. Use the token in GraphQL requests such as (replacing url and token)
```
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1192460_
