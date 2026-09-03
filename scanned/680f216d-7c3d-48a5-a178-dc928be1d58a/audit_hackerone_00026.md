# [M] [Vertical Privilege Escalation] User can Unapproved any Approved Translation at [/translations/unapprove/]

## Summary
Severity: Medium (CVSS 6.5)
Program: Mozilla
Weakness: Privilege Escalation
Reporter: adilnbabras
State: resolved
Disclosed: 2026-04-10T01:13:22.605Z
Source: https://hackerone.com/reports/3020021

## Details
Hi, team. During testing, I discovered that only privileged users or translation owners can unapprove an approved translation, but due to logical errors, any logged-in user can unapprove any approved translation. 

## Steps To Reproduce:
- Go to `https://mozilla-pontoon-staging.herokuapp.com/` and log in to your account.

- Click on `Teams` and select any team from the menu.

{F4104059}

{F4104060}

- Now, from the next menu, select any project and then select any resource you want.

{F4104061}

{F4104062}

- After that, you will have a list of strings that you can translate.

{F4104063}

- Select any string and you will see an already approved translation with green `tick` symbol.

{F4104065}

- You can check that you can't unapprove that translation because you don't have the required privileges.

- Now, prepare your proxy to capture requests and reload that page.

- In proxy history, you will see a request to the`/get-history/` endpoint. Like this one.

{F4104071}

- In response to that request, you will find the approved translation `ID`.  Copy that.

{F4104072}

- Now replace the session cookies, Anti-CSRF token, and Translation ID in this request and send this request.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3020021_
