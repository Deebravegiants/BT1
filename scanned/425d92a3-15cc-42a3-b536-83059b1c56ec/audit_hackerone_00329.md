# [M] SSRF in CI after first run

## Summary
Severity: Medium
Program: GitLab
Weakness: Server-Side Request Forgery (SSRF)
Reporter: plazmaz
State: resolved
Disclosed: 2019-04-12T19:57:38.977Z
Source: https://hackerone.com/reports/369451

## Details
> NOTE! Thanks for submitting a report! Please replace *all* the [square] sections below with the pertinent details. Remember, the more detail you provide, the easier it is for us to triage and respond quickly, so be sure to take your time filling out the report!

**Summary:** 
During the first run, the CI pipeline seems to defend against SSRF properly, however when a build is re-run a second time, I am able to access internal metadata endpoints for digitalocean

**Description:**
The following resources are accessible on the second run of a CI build. For instance,
`http://169.254.169.254/metadata/v1.json` 
and `http://169.254.169.254/metadata/v1/`
are both visible.


## Steps To Reproduce:

(Add details for how we can reproduce the issue)

  1. Create a `.gitlab-ci.yml`. This was my PoC:

```
# This file is a template, and might need editing before it works on your project.
# Official framework image. Look for the different tagged releases at:
# https://hub.docker.com/r/library/node/tags/
image: node:latest

# This folder is cached between builds
# http://docs.gitlab.com/ce/ci/yaml/README.html#cache
cache:
  paths:
  - node_modules/

test:
  stage: test
  script:
    - npm install
    - npm test

pack:
  stage: deploy
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/369451_
