# [H] Eclipse Milo vulnerable to Resource Exhaustion (Denial of Service)

## Summary
Severity: High
Advisory: GHSA-fph9-f5r6-vhqf
CVE: CVE-2022-25897
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-fph9-f5r6-vhqf
Type: github-advisory

## Affected
- Maven: `org.eclipse.milo:sdk-server` — affected >=0 <0.6.8

## Details
### Impact

Denial of Service

### Details

OPC UA specification describes a concept named _Subscriptions_. _Subscriptions_ monitor a set of _Monitored Items_ for _Notifications_ and return them to the _Client_ in response to _Publish_ requests. The server notifies the client about changes only in case the value is changed. Each monitored item is configured on a subscription, each subscription is linked to a single OPC UA session. Most OPC UA implementations set many controls and limitations for excessive memory consumption. For example:

* What is the maximum allowed number of concurrent sessions
* For each active sessions - what is the maximum allowed number of concurrent subscription per a single session
* For each active subscription - what is the maximum allowed number of concurrent monitored items per a single subscription

Clarity Research discovered a unique way to bypass those restrictions and fill up the OPC UA server process memory.

The close session request closes a connected session. A `deleteSubscription` flag is also sent in that message and determines whether the server should save the subscriptions for a future session reconnection or discard them upon session termination. If the `deleteSubscription` flag is `False` the server will store the subscriptions thus filling up the memory in an unlimited manner.

Sending multiple subscribe requests with multiple monitored items from multiple sessions will quickly fill up the process memory until the server crashes.

To trigger this bug all is needed is to create many sessions with subscriptions and monitored items without ever deleting the monitored items. Eventually these allocations will consume all the available process memory which will lead to a crash and denial of service condition.

Clarity PoC does:
```
while True:
    Open a valid OPC UA session
    Create multiple subscriptions
    Add monitored items to each subscription
    Close the session with the DeleteSubscriptions flag = False
````

### Acknowledgement

We would like to thanks Vera Mens, Uri Katz, @sharonbrizinov of Team82 ([Claroty Research](https://claroty.com/)) for this report.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Eclipse Milo repository](https://github.com/eclipse/milo/issues)
* Email us at [milo-dev](https://accounts.eclipse.org/mailing-list/milo-dev)

## References
- https://github.com/eclipse/milo/security/advisories/GHSA-fph9-f5r6-vhqf
- https://nvd.nist.gov/vuln/detail/CVE-2022-25897
- https://github.com/eclipse/milo/issues/1030
- https://github.com/eclipse/milo/pull/1031
- https://github.com/eclipse/milo/commit/4534381760d7d9f0bf00cbf6a8449bb0d13c6ce5
- https://github.com/eclipse/milo
- https://security.snyk.io/vuln/SNYK-JAVA-ORGECLIPSEMILO-2990191
