# [H] Unauthenticated SSRF in Voxtelesys integration ('checkUrlForSsrf' Bypass via DNS rebinding)

## Summary
Severity: High (CVSS 8.6)
Program: Rocket.Chat
Weakness: Server-Side Request Forgery (SSRF)
Reporter: button142857
State: resolved
Disclosed: 2026-07-29T01:48:49.623Z
CVE: CVE-2024-39713
Source: https://hackerone.com/reports/3473145

## Details
**Summary:** 
Rocket.Chat version 7.13.2 contains an SSRF vulnerability caused by a DNS rebinding attack, which allows access to internal hosts and reading of their responses.
This issue further bypasses the fix for CVE-2024-39713.

Rocket.Chat provides SMS integration features using Twilio and Voxtelesys, which can be used to access external media and retrieve files. During this process, the `checkUrlForSsrf` function is used to verify that a URL does not point to an internal host. However, this function is vulnerable to DNS rebinding attacks, and when a URL whose domain is controlled by an attacker is submitted, the check can be bypassed, potentially allowing access to internal hosts that would otherwise be unreachable.

**Details:**
In my test environment, I set up an httpbin server on the same LAN as the Rocket.Chat server.
The httpbin server is running at 192.168.100.14:80, and an attacker cannot reach this server directly from outside. 
In addition, a DNS server for performing a DNS rebinding attack was deployed within the same LAN, and the Rocket.Chat server was configured to use it for name resolution. 
When resolving the name `conamikan.test`, the DNS server returns an external server address (1.1.1.1) with TTL=0 on the first request, and returns 192.168.100.14 on the second and subsequent requests. All other DNS queries are forwarded to 8.8.8.8. The specific implementation is provided in the attachment.
In a realistic scenario, when accessing a domain controlled by an attacker, name resolution would be performed by the attacker’s DNS server. Therefore, this environment is sufficient for verifying DNS rebinding attacks.

Step 0: 
As a prerequisite, Voxtelesys must be enabled in the SMS settings.
{F5138160}

Step 1: 
An attacker can trigger the SSRF by executing the following script. No authentication is required. (Set <Rocket.Chat hostIP> according to your environment.)
```
POST "http://<Rocket.Chat hostIP>/api/v1/livechat/sms-incoming/voxtelesys" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+15551112222",
    "to": "+15550001111",
    "body": "Hello from Voxtelesys",
    "received_at": "2024-01-01T00:00:00Z",
    "media": [
      "http://conamikan.test"
    ]
  }'
```
At this point, an SSRF request to the internal server has already been performed.
{F5138169}

Step 2: 
A LiveChat agent user can download and view the response from the chat room.
{F5138172}

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3473145_
