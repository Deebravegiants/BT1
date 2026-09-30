# [?] [Debug UI] Fix the start_height UI crash. (#11177)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-04-29
Source: https://github.com/near/nearcore/commit/549f4b5da2a6bba7ac470e70a95a792df2594ceb
Type: security-commit

## Details
[Debug UI] Fix the start_height UI crash. (#11177)

Also run "npm run fix" and fix issues.

## Patch
### chain/jsonrpc/res/sync.html
```diff
@@ -90,11 +90,11 @@
                     let to = sync_status.HeaderSync.highest_height;
                     $('.js-header-sync').text("Header sync - " + from + " -> " + to + ":    " + (to - from) + " remaining");
                 }
-                if ('BodySync' in sync_status) {
+                if ('BlockSync' in sync_status) {
                     $('.js-header-sync').text("Header sync - ✅.");
                     $('.js-state-sync').text("State sync - ✅.");
-                    let from = sync_status.BodySync.current_height;
-                    let to = sync_status.BodySync.highest_height;
+                    let from = sync_status.BlockSync.current_height;
+                    let to = sync_status.BlockSync.highest_height;
                     $('.js-block-sync').text("Block sync - " + from + " -> " + to + ":    " + (to - from) + " remaining");
                 }
             }
```

### tools/debug-ui/src/ClusterNodeView.tsx
```diff
@@ -116,7 +116,7 @@ function syncStatusToText(syncStatus: SyncStatusResponse): string {
     if ('StateSync' in status) {
         return 'State sync';
     }
-    return `Body sync ${status.BodySync.start_height} -> ${status.BodySync.highest_height}`;
+    return `Block sync ${status.BlockSync.start_height} -> ${status.BlockSync.highest_height}`;
 }
 
 function booleanArrayToIndexList(array: boolean[]): number[] {
```

### tools/debug-ui/src/LandingPage.tsx
```diff
@@ -1,7 +1,6 @@
 import { useState } from 'react';
-import { useNavigate } from 'react-router-dom';
+import { useNavigate, Link } from 'react-router-dom';
 import './LandingPage.scss';
-import { Link } from 'react-router-dom';
 
 export const LandingPage = () => {
     const [addr, setAddr] = useState('');
```

### tools/debug-ui/src/RoutingTableView.tsx
```diff
@@ -1,5 +1,5 @@
 import { useQuery } from '@tanstack/react-query';
-import { toHumanTime, formatDurationInMillis } from './utils';
+import { formatDurationInMillis } from './utils';
 import { fetchRoutingTable } from './api';
 import './RoutingTableView.scss';
 
@@ -25,7 +25,7 @@ export const RoutingTableView = ({ addr }: RoutingTableViewProps) => {
     const peerLabels = routingInfo.edge_cache.peer_labels;
 
     const routable_peers = Object.keys(routingInfo.my_distances);
-    routable_peers.sort((a, b) => peerLabels[a] > peerLabels[b] ? 1 : -1);
+    routable_peers.sort((a, b) => (peerLabels[a] > peerLabels[b] ? 1 : -1));
 
     const direct_peers: string[] = [];
     const disconnected_peers: string[] = [];
@@ -38,12 +38,14 @@ export const RoutingTableView = ({ addr }: RoutingTableViewProps) => {
         }
     });
 
-    direct_peers.sort((a, b) => peerLabels[a] > peerLabels[b] ? 1 : -1);
-    disconnected_peers.sort((a, b) => peerLabels[a] > peerLabels[b] ? 1 : -1);
+    direct_peers.sort((a, b) => (peerLabels[a] > peerLabels[b] ? 1 : -1));
+    disconnected_peers.sort((a, b) => (peerLabels[a] > peerLabels[b] ? 1 : -1));
 
     return (
         <div className="routing-table-view">
-            <p><b>Routable Peers</b></p>
+            <p>
+                <b>Routable Peers</b>
+            </p>
             <table>
                 <thead>
                     <th>Peer ID</th>
@@ -63,8 +65,10 @@ export const RoutingTableView = ({ addr }: RoutingTableViewProps) => {
                     })}
                 </tbody>
             </table>
-            <br/>
-            <p><b>Direct Peers</b></p>
+            <br />
+            <p>
+                <b>Direct Peers</b>
+            </p>
             <table>
                 <thead>
                     <th>Peer ID</th>
@@ -83,14 +87,22 @@ export const RoutingTableView = ({ addr }: RoutingTableViewProps) => {
                                 <td>{peer_id.substring(8, 14)}...</td>
                                 <td>{peer_label}</td>
                                 <td>{peer_distances.distance.map((x) => x ?? '_').join(', ')}</td>
-                                <td>{peer_distances.min_nonce} ({formatDurationInMillis(Date.now() - peer_distances.min_nonce * 1000)})</td>
+                                <td>
+                                    {peer_distances.min_nonce} (
+                                    {formatDurationInMillis(
+                                        Date.now() - peer_distances.min_nonce * 1000
+                                    )}
+                                    )
+                                </td>
                             </tr>
                         );
                     })}
                 </tbody>
             </table>
-            <br/>
-            <p><b>Disconnected Peers</b></p>
+            <br />
+            <p>
+                <b>Disconnected Peers</b>
+            </p>
             <table>
                 <thead>
                     <th>Peer ID</th>
@@ -106,7 +118,9 @@ export const RoutingTableView = ({ addr }: RoutingTableViewProps) => {
                             <tr key={peer_label}>
                                 <td>{peer_id.substring(8, 14)}...</td>
                                 <td>{peer_label}</td>
-                                <td>{nonce} ({formatDurationInMillis(Date.now() - nonce * 1000)})</td>
+                                <td>
+                                    {nonce} ({formatDurationInMillis(Date.now() - nonce * 1000)})
+                                </td>
                             </tr>
                         );
                     })}
```

### tools/debug-ui/src/SnapshotHostsView.tsx
```diff
@@ -1,5 +1,4 @@
 import { useQuery } from '@tanstack/react-query';
-import { toHumanTime } from './utils';
 import { fetchSnapshotHosts } from './api';
 import './SnapshotHostsView.scss';
 
@@ -32,18 +31,16 @@ export const SnapshotHostsView = ({ addr }: SnapshotHostsViewProps) => {
                     <th>Sync Hash</th>
                 </thead>
                 <tbody>
-                    {snapshot_hosts.hosts.map(
-                        (host) => {
-                            return (
-                                <tr key={host.peer_id}>
-                                    <td>{host.peer_id}</td>
-                                    <td>{JSON.stringify(host.shards)}</td>
-                                    <td>{host.epoch_height}</td>
-                                    <td>{host.sync_hash}</td>
-                                </tr>
-                            );
-                        }
-                    )}
+                    {snapshot_hosts.hosts.map((host) => {
+                        return (
+                            <tr key={host.peer_id}>
+                                <td>{host.peer_id}</td>
+                                <td>{JSON.stringify(host.shards)}</td>
+                                <td>{host.epoch_height}</td>
+                                <td>{host.sync_hash}</td>
+                            </tr>
+                        );
+                    })}
                 </tbody>
             </table>
         </div>
```

### tools/debug-ui/src/api.tsx
```diff
@@ -126,7 +126,7 @@ export type SyncStatusView =
       }
     | 'StateSyncDone'
     | {
-          BodySync: {
+          BlockSync: {
               start_height: number;
               current_height: number;
               highest_height: number;
@@ -299,13 +299,13 @@ export interface EdgeView {
     peer0: string;
     peer1: string;
     nonce: number;
-};
+}
 
 export interface LabeledEdgeView {
     peer0: number;
     peer1: number;
     nonce: number;
-};
+}
 
 export interface EdgeCacheView {
     peer_labels: { [peer_id: string]: number };
@@ -321,7 +321,7 @@ export interface RoutingTableView {
     edge_cache: EdgeCacheView;
     local_edges: { [peer_id: string]: EdgeView };
     peer_distances: { [peer_id: string]: PeerRoutesView };
-    my_distances: { [peer_id: string]:  number };
+    my_distances: { [peer_id: string]: number };
 }
 
 export interface RoutingTableResponse {
@@ -331,14 +331,14 @@ export interface RoutingTableResponse {
 }
 
 export interface SnapshotHostInfoView {
-    peer_id: string,
-    sync_hash: string,
-    epoch_height: number,
-    shards: number[],
+    peer_id: string;
+    sync_hash: string;
+    epoch_height: number;
+    shards: number[];
 }
 
 export interface SnapshotHostsView {
-    hosts: SnapshotHostInfoView[],
+    hosts: SnapshotHostInfoView[];
 }
 
 export interface SnapshotHostsResponse {
@@ -451,16 +451,12 @@ export async function fetchRecentOutboundConnections(
     return await response.json();
 }
 
-export async function fetchRoutingTable(
-    addr: string
-): Promise<RoutingTableResponse> {
+export async function fetchRoutingTable(addr: string): Promise<RoutingTableResponse> {
     const response = await fetch(`http://${addr}/debug/api/network_routes`);
     return await response.json();
 }
 
-export async function fetchSnapshotHosts(
-    addr: string
-): Promise<SnapshotHostsResponse> {
+export async function fetchSnapshotHosts(addr: string): Promise<SnapshotHostsResponse> {
     const response = await fetch(`http://${addr}/debug/api/snapshot_hosts`);
     return await response.json();
 }
```

### tools/debug-ui/src/log_visualizer/events.ts
```diff
@@ -57,12 +57,17 @@ export class EventItem {
             const secondBracket = /[({]/.exec(afterFirstParens);
             if (secondBracket !== null) {
                 this.subtitle = afterFirstParens.substring(0, secondBracket.index);
-                if (this.subtitle === "DelayedAction"
-                    || this.subtitle === "Task"
-                    || this.subtitle === "AsyncComputation") {
+                if (
+                    this.subtitle === 'DelayedAction' ||
+                    this.subtitle === 'Task' ||
+                    this.subtitle === 'AsyncComputation'
+                ) {
                     // Special logic for DelayedAction and Task, where we're more interested
                     // in the name, which is printed in the parens.
-                    this.subtitle = afterFirstParens.substring(secondBracket.index + 1, afterFirstParens.length - 1);
+                    this.subtitle = afterFirstParens.substring(
+                        secondBracket.index + 1,
+                        afterFirstParens.length - 1
+                    );
                 }
             } else {
                 this.subtitle = afterFirstParens;
@@ -188,20 +193,24 @@ export class EventItemCollection {
                     current_event: string;
                     current_time_ms: number;
                 };
-                const startData = JSON.parse(line.substring(startIndex + startMarker.length)) as EventStartLogLineData;
+                const startData = JSON.parse(
+                    line.substring(startIndex + startMarker.length)
+                ) as EventStartLogLineData;
                 totalEventCount = startData.total_events;
                 const event = new EventItem(
                     startData.current_index,
                     parentIds[startData.current_index] ?? null,
                     startData.current_time_ms,
-                    startData.current_event,
+                    startData.current_event
                 );
                 items.add(event);
             } else if (endIndex != -1) {
                 type EventEndLogLineData = {
                     total_events: number;
                 };
-                const endData = JSON.parse(line.substring(endIndex + endMarker.length)) as EventEndLogLineData;
+                const endData = JSON.parse(
+                    line.substring(endIndex + endMarker.length)
+                ) as EventEndLogLineData;
                 for (let i = totalEventCount; i < endData.total_events; i++) {
                     parentIds[i] = items.lastEvent()!.id;
                 }
```

### tools/debug-ui/src/log_visualizer/layout.ts
```diff
@@ -149,13 +149,20 @@ export class Layouts {
                 }
             }
             let parentItem = item.parentId === null ? null : items.get(item.parentId);
-            if (parentItem !== null && items.isAttachedToParent(parentItem.id) && parentItem.parentId !== null) {
+            if (
+                parentItem !== null &&
+                items.isAttachedToParent(parentItem.id) &&
+                parentItem.parentId !== null
+            ) {
                 parentItem = items.get(parentItem.parentId);
             }
             if (parentItem !== null) {
                 // Make sure that the child item is always placed below the parent; otherwise the arrows would
                 // point backwards.
-                nextRowForColumn[item.column] = Math.max(nextRowForColumn[item.column], parentItem.row + 1);
+                nextRowForColumn[item.column] = Math.max(
+                    nextRowForColumn[item.column],
+                    parentItem.row + 1
+                );
             }
             item.row = nextRowForColumn[item.column]++;
             if (item.row >= this.rows.length) {
```
