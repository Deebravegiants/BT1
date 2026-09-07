# [M] Bypass report submit restriction/ban using the API key

## Summary
Severity: Medium (CVSS 6.1)
Program: HackerOne
Weakness: Privilege Escalation
Reporter: light3r
State: resolved
Disclosed: 2023-10-29T11:23:39.167Z
Source: https://hackerone.com/reports/2081930

## Details
#Description:

* Banned researcher allows to submit reports through the API key, when user ban reports on his account he can't submit any reports to any programs until his ban time is gone, I was able to submit the report through the API key

##Steps to reproduce:

* I contacted the support then they banned my account to send reports as shown below:

{F2531260}

* Then after they banned my account I wasn't able to send any report also when I create directly from the request I receives 403 forbidden

* I go to create a sandbox program and API key:

{F2531264}

{F2531263}

* I navigate to the documentation:

https://api.hackerone.com/hacker-resources/#reports-create-report

* So after creating the API key using the below request/command I was able to submit the reports to any program without any restrictions on reports

```bash
curl "https://api.hackerone.com/v1/hackers/reports"   -X POST   -u "testhackerone-creative:pYnONekvxUTvHbKF7Jp64qh9STIhhdXvKmefWOeR8YU="   -H 'Content-Type: application/json'   -H 'Accept: application/json'   -d @- <<EOD
{
  "data": {
    "type": "report",
    "attributes": {
      "team_handle": "HackerOne-test_h1b",
      "title": "string",
      "vulnerability_information": "test tst tst",
      "impact": "tst tst",
      "severity_rating": "none",
      "weakness_id": 1
    }
  }
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2081930_
