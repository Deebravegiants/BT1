# [M] Banned user still has access to their deleted account via HackerOne's API using their API key

## Summary
Severity: Medium (CVSS 5.0)
Program: HackerOne
Weakness: Improper Access Control - Generic
Reporter: mrmax4o4
State: resolved
Disclosed: 2025-07-14T20:50:35.256Z
Source: https://hackerone.com/reports/1577940

## Details
Hello team,

##Summary:

When a user's account gets banned (permanently), he is no longer able to submit reports, and as soon as there are no pending payouts the account will be deleted. The user won't have access to the account(login) or show his profile. By using a previously generated API token(before the ban) the user will be able to:

* Get Reports
* Get Balance
* Get Earnings
* Get Payouts
* Get Weaknesses
* Get Programs

Generally, the user will be able to do the following actions https://api.hackerone.com/hacker-reference/#hacker-reference.

##Steps to reproduce:

- Create a new account
- Ban the account permanently (I am waiting for approval and I will share an API token for a banned account).

let's assume the
- Username: `mrtst`
- API token: `XXXXXXXXXXXXXXXXXXXX=`

**Exploit:**

- Get Reports (Get a single report also):

>curl "https://api.hackerone.com/v1/hackers/me/reports" -X GET -u "mrtst:XXXXXXXXXXXXXXXXXXXX=" -H 'Accept: application/json'

- Get Balance:

> curl "https://api.hackerone.com/v1/hackers/payments/balance" -X GET -u "mrtst:XXXXXXXXXXXXXXXXXXXX=" -H 'Accept: application/json'

- Get Earnings:

>curl "https://api.hackerone.com/v1/hackers/payments/earnings" -X GET -u "mrtst:XXXXXXXXXXXXXXXXXXXX=" -H 'Accept: application/json'


_Trimmed to 38 lines — full report: https://hackerone.com/reports/1577940_
