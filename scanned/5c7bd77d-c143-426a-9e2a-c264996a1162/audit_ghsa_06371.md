# [M] Yamcs: Insecure Direct Object Reference (IDOR) in PacketsApi allows unprivileged users to dump all telemetry packets

## Summary
Severity: Medium
Advisory: GHSA-8xjq-pr36-ccgf
CVE: CVE-2026-55548
CWE: CWE-284, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-8xjq-pr36-ccgf
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=5.13.0 <5.13.2
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.8

## Details
## Summary
The `PacketsApi.exportPackets` endpoint in Yamcs fails to properly enforce object-level privileges (`ReadPacket`) when an API request omits specific packet names. As a result, an attacker with a low-privileged account (or any authenticated user with zero privileges) can dump the entire archive of raw telemetry packets for a Yamcs instance. This leads to a massive Information Disclosure of sensitive mission telemetry, completely bypassing the intended Role-Based Access Control (RBAC) model.

## Vulnerability Details
In `yamcs-core/src/main/java/org/yamcs/http/api/PacketsApi.java`, the `exportPackets` method processes requests to export raw packets from the `tm` (telemetry archive) table.

```java
    @Override
    public void exportPackets(Context ctx, ExportPacketsRequest request, Observer<HttpBody> observer) {
        String instance = InstancesApi.verifyInstance(request.getInstance());

        Set<String> nameSet = new HashSet<>(request.getNameList());
        ctx.checkObjectPrivileges(ObjectPrivilegeType.ReadPacket, nameSet);

        SqlBuilder sqlb = new SqlBuilder(XtceTmRecorder.TABLE_NAME);
        
        // ... time filters ...

        if (request.getNameCount() > 0) {
            sqlb.whereColIn("pname", nameSet);
        }
        String sql = sqlb.toString();
        // ...
```
The method attempts to verify privileges using `ctx.checkObjectPrivileges(ObjectPrivilegeType.ReadPacket, nameSet)`. However, if the `request.getNameList()` is empty (i.e., the attacker does not specify any packet names to filter by), `nameSet` is empty. The `checkObjectPrivileges` method loops over this empty set and successfully passes without throwing a `ForbiddenException`. 

Since `request.getNameCount()` is 0, no `WHERE pname IN (...)` filter is added to the SQL query. The resulting `sql` query becomes a `SELECT * FROM tm` (with optional time filters).

Finally, the query is executed and the results are streamed back to the user:
```java
        StreamFactory.stream(instance, sql, sqlb.getQueryArguments(), new StreamSubscriber() {

            @Override
            public void onTuple(Stream stream, Tuple tuple) {
                if (observer.isCancelled()) {
                    stream.close();
                    return;
                }

                byte[] raw = (byte[]) tuple.getColumn(StandardTupleDefinitions.TM_PACKET_COLUMN);
                HttpBody body = HttpBody.newBuilder()
                        .setData(ByteString.copyFrom(raw))
                        .build();
                observer.next(body);
            }
            // ...
```
Crucially, unlike the `streamPackets` or `exportPacket` methods (which explicitly check `ctx.user.hasObjectPrivilege` for each packet retrieved before returning them), the `onTuple` handler in `exportPackets` **blindly streams all retrieved packets to the user without any per-row authorization checks**. 

Thus, a user who possesses no `ReadPacket` privileges at all can easily bypass authorization and extract all telemetry data from the archive.

## Steps to Reproduce
1. Start the Yamcs server (e.g., using the `simulation` example) with authentication enforced.
2. Log in as a low-privileged user (or use their credentials) who does **not** have the `ReadPacket` privilege.
3. Send an HTTP GET request to the export packets endpoint without specifying any `name` parameters:
   ```bash
   curl -v -u low_priv_user:password "http://localhost:8090/api/archive/simulator:exportPackets" -o dumped_packets.raw
   ```
4. Observe that the server responds with HTTP `200 OK` and streams all raw packets to the response, saving them to `dumped_packets.raw`. 
5. The downloaded file contains raw CCSDS Space Packets (binary telemetry data).
6. Contrast this with an attempt to fetch a specific packet (or calling `listPackets` for an unauthorized packet), which correctly enforces authorization and rejects the request.

## Impact
Telemetry packets contain the core mission data, vehicle health status, and sensitive measurements (CCSDS Protocol data). This vulnerability completely breaks the access control model for telemetry data, allowing any authenticated user to exfiltrate all historical telemetry packets from the database. In an aerospace or mission-critical environment, this represents a severe data leak (Massive Information Disclosure) of proprietary or classified spacecraft data.

## Remediation
Ensure that `exportPackets` enforces the same per-row privilege checks as `streamPackets`. 
Update the `onTuple` handler to check the user's privileges before emitting each packet:

```java
            @Override
            public void onTuple(Stream stream, Tuple tuple) {
                if (observer.isCancelled()) {
                    stream.close();
                    return;
                }

                // FIX: Retrieve packet name and check authorization
                String pname = (String) tuple.getColumn(XtceTmRecorder.PNAME_COLUMN);
                if (ctx.user.hasObjectPrivilege(ObjectPrivilegeType.ReadPacket, pname)) {
                    byte[] raw = (byte[]) tuple.getColumn(StandardTupleDefinitions.TM_PACKET_COLUMN);
                    HttpBody body = HttpBody.newBuilder()
                            .setData(ByteString.copyFrom(raw))
                            .build();
                    observer.next(body);
                }
            }
```

## System Information
- **Affected Versions:** 5.13.0 (Latest Release), 5.12.x, and current `master` branch.
- **Tested Revision (master):** `309218c651680f79df11a8d0f8628f7033f98a83` 
- **Vulnerability Type:** Insecure Direct Object Reference (IDOR) / Logical Authorization Bypass

## PoC Images:

- Check version:
<img width="1157" height="489" alt="image" src="https://github.com/user-attachments/assets/58608222-b76f-4eb4-8e57-423523062992" />

- Check privilege of user:
<img width="1439" height="953" alt="image" src="https://github.com/user-attachments/assets/aa7e55f2-2460-4f24-8b6f-d461d2499a6f" />
<img width="1214" height="224" alt="image" src="https://github.com/user-attachments/assets/e9123ae3-a194-462d-a5ca-2c0b1cc9cc6f" />


- Exploit:


<img width="1728" height="685" alt="image" src="https://github.com/user-attachments/assets/0c7b3099-44d6-4392-bbaa-8e84cc151784" />

<img width="1768" height="797" alt="image" src="https://github.com/user-attachments/assets/df4016a5-d460-4611-a34a-8c0d206edd9c" />

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-8xjq-pr36-ccgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-55548
- https://github.com/yamcs/yamcs/commit/b566beceba98cc35514b0e1519be126b8c5a0438
- https://github.com/yamcs/yamcs/commit/c743cc3acf5b5c53ff5181b94eacc21340f70dd9
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.12.8
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.13.2
