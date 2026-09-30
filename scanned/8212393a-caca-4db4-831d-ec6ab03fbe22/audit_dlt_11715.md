# [?] Fix mock websocket race condition, add optional mempool blocks waiter

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-02-07
Source: https://github.com/mempool/mempool/commit/7dec74404cfa4c90fa48db22b9f6b8d17fae4b62
Type: security-commit

## Details
Fix mock websocket race condition, add optional mempool blocks waiter

## Patch
### frontend/cypress/support/websocket.ts
```diff
@@ -32,7 +32,7 @@ export const mockWebSocketV2 = () => {
 		const winWebSocket = win.WebSocket;
 		cy.stub(win, 'WebSocket').callsFake((url) => {
 			console.log(url);
-			if ((new URL(url).pathname.indexOf('/sockjs-node/') !== 0)) {
+			if ((new URL(url).pathname.indexOf('/sockjs-node/') !== 0) && (new URL(url).pathname.indexOf('/ng-cli-ws') !== 0)) {
 				const { server, websocket } = createMock(url);
 
 				win.mockServer = server;
@@ -117,10 +117,16 @@ export const receiveWebSocketMessageFromServer = ({
 };
 
 
+const MOCK_SOCKET_WAIT_TIMEOUT_MS = 5000;
+
 export const emitMempoolInfo = ({
 	params
 }: { params?: any } = {}) => {
-	cy.window().then((win) => {
+	cy.window({ timeout: MOCK_SOCKET_WAIT_TIMEOUT_MS })
+		.should((win) => {
+			expect(win.mockSocket, 'mockSocket to be set (app should open WebSocket within timeout)').to.not.be.undefined;
+		})
+		.then((win) => {
 		//TODO: Refactor to take into account different parameterized mocking scenarios
 		switch (params.network) {
 			//TODO: Use network specific mocks
@@ -133,7 +139,6 @@ export const emitMempoolInfo = ({
 
 		switch (params.command) {
 			case 'init': {
-				win.mockSocket.send('{"conversions":{"USD":32365.338815782445}}');
 				cy.readFile('cypress/fixtures/mainnet_live2hchart.json', 'utf-8').then((fixture) => {
 					win.mockSocket.send(JSON.stringify(fixture));
 				});
@@ -159,7 +164,11 @@ export const emitMempoolInfo = ({
 		}
 	});
     cy.waitForSkeletonGone();
-    return cy.get('#mempool-block-0');
+		if (!params.waitForMempoolBlocks) {
+			return
+		} else {
+			return cy.get('#mempool-block-0');
+		}
 };
 
 export const dropWebSocket = (() => {
```
