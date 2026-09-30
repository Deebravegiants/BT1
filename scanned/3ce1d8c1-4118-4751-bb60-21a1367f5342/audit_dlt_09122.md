# [?] Merge branch 'v2.0' into fix/crash-if-terminate-is-undefined

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2025-03-12
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/cf00e6be35f30d2e0b0f19583c0918acb2ae44ad
Type: security-commit

## Details
Merge branch 'v2.0' into fix/crash-if-terminate-is-undefined

## Patch
### packages/core/src/constants/relayer.ts
```diff
@@ -43,3 +43,8 @@ export const TRANSPORT_TYPES = {
   link_mode: "link_mode",
   relay: "relay",
 } as const;
+
+export const MESSAGE_DIRECTION = {
+  inbound: "inbound",
+  outbound: "outbound",
+} as const;
```

### packages/core/src/controllers/messages.ts
```diff
@@ -1,10 +1,21 @@
 import { generateChildLogger, getLoggerContext, Logger } from "@walletconnect/logger";
 import { ICore, IMessageTracker, MessageRecord } from "@walletconnect/types";
 import { hashMessage, mapToObj, objToMap, getInternalError } from "@walletconnect/utils";
-import { CORE_STORAGE_PREFIX, MESSAGES_CONTEXT, MESSAGES_STORAGE_VERSION } from "../constants";
+import {
+  CORE_STORAGE_PREFIX,
+  MESSAGE_DIRECTION,
+  MESSAGES_CONTEXT,
+  MESSAGES_STORAGE_VERSION,
+} from "../constants";
 
 export class MessageTracker extends IMessageTracker {
   public messages = new Map<string, MessageRecord>();
+  /**
+   * stores messages that have not been acknowledged by the implementing client
+   * this is used to prevent losing messages in race conditions such as
+   * when a message is received by the relayer before the implementing client is ready to receive it
+   */
+  public messagesWithoutClientAck = new Map<string, MessageRecord>();
   public name = MESSAGES_CONTEXT;
   public version = MESSAGES_STORAGE_VERSION;
 
@@ -25,7 +36,10 @@ export class MessageTracker extends IMessageTracker {
         if (typeof messages !== "undefined") {
           this.messages = messages;
         }
-
+        const messagesWithoutClientAck = await this.getRelayerMessagesWithoutClientAck();
+        if (typeof messagesWithoutClientAck !== "undefined") {
+          this.messagesWithoutClientAck = messagesWithoutClientAck;
+        }
         this.logger.debug(`Successfully Restored records for ${this.name}`);
         this.logger.trace({ type: "method", method: "restore", size: this.messages.size });
       } catch (e) {
@@ -45,7 +59,18 @@ export class MessageTracker extends IMessageTracker {
     return this.storagePrefix + this.version + this.core.customStoragePrefix + "//" + this.name;
   }
 
-  public set: IMessageTracker["set"] = async (topic, message) => {
+  get storageKeyWithoutClientAck() {
+    return (
+      this.storagePrefix +
+      this.version +
+      this.core.customStoragePrefix +
+      "//" +
+      this.name +
+      "_withoutClientAck"
+    );
+  }
+
+  public set: IMessageTracker["set"] = async (topic, message, direction) => {
     this.isInitialized();
     const hash = hashMessage(message);
     let messages = this.messages.get(topic);
@@ -57,6 +82,15 @@ export class MessageTracker extends IMessageTracker {
     }
     messages[hash] = message;
     this.messages.set(topic, messages);
+    // Only store messages without client ack for inbound messages
+    if (direction === MESSAGE_DIRECTION.inbound) {
+      const messagesWithoutClientAck = this.messagesWithoutClientAck.get(topic) || {};
+      this.messagesWithoutClientAck.set(topic, {
+        ...messagesWithoutClientAck,
+        [hash]: message,
+      });
+    }
+
     await this.persist();
     return hash;
   };
@@ -70,16 +104,45 @@ export class MessageTracker extends IMessageTracker {
     return messages;
   };
 
+  public getWithoutAck: IMessageTracker["getWithoutAck"] = (topics) => {
+    this.isInitialized();
+    const messages: Record<string, string[]> = {};
+    for (const topic of topics) {
+      const messagesWithoutClientAck = this.messagesWithoutClientAck.get(topic) || {};
+      messages[topic] = Object.values(messagesWithoutClientAck);
+    }
+    return messages;
+  };
+
   public has: IMessageTracker["has"] = (topic, message) => {
     this.isInitialized();
     const messages = this.get(topic);
     const hash = hashMessage(message);
     return typeof messages[hash] !== "undefined";
   };
 
+  public ack: IMessageTracker["ack"] = async (topic, message) => {
+    this.isInitialized();
+    const messages = this.messagesWithoutClientAck.get(topic);
+    if (typeof messages === "undefined") {
+      return;
+    }
+
+    const hash = hashMessage(message);
+
+    delete messages[hash];
+    if (Object.keys(messages).length === 0) {
+      this.messagesWithoutClientAck.delete(topic);
+    } else {
+      this.messagesWithoutClientAck.set(topic, messages);
+    }
+    await this.persist();
+  };
+
   public del: IMessageTracker["del"] = async (topic) => {
     this.isInitialized();
     this.messages.delete(topic);
+    this.messagesWithoutClientAck.delete(topic);
     await this.persist();
   };
 
@@ -92,15 +155,34 @@ export class MessageTracker extends IMessageTracker {
     );
   }
 
+  private async setRelayerMessagesWithoutClientAck(
+    messages: Map<string, MessageRecord>,
+  ): Promise<void> {
+    await this.core.storage.setItem<Record<string, MessageRecord>>(
+      this.storageKeyWithoutClientAck,
+      mapToObj(messages),
+    );
+  }
+
   private async getRelayerMessages(): Promise<Map<string, MessageRecord> | undefined> {
     const messages = await this.core.storage.getItem<Record<string, MessageRecord>>(
       this.storageKey,
     );
     return typeof messages !== "undefined" ? objToMap(messages) : undefined;
   }
 
+  private async getRelayerMessagesWithoutClientAck(): Promise<
+    Map<string, MessageRecord> | undefined
+  > {
+    const messages = await this.core.storage.getItem<Record<string, MessageRecord>>(
+      this.storageKeyWithoutClientAck,
+    );
+    return typeof messages !== "undefined" ? objToMap(messages) : undefined;
+  }
+
   private async persist() {
     await this.setRelayerMessages(this.messages);
+    await this.setRelayerMessagesWithoutClientAck(this.messagesWithoutClientAck);
   }
 
   private isInitialized() {
```

### packages/core/src/controllers/pairing.ts
```diff
@@ -323,34 +323,35 @@ export class Pairing implements IPairing {
       // messages of certain types should be ignored as they are handled by their respective SDKs
       if (this.ignoredPayloadTypes.includes(this.core.crypto.getPayloadType(message))) return;
 
-      const payload = await this.core.crypto.decode(topic, message);
-
       try {
+        const payload = await this.core.crypto.decode(topic, message);
+
         if (isJsonRpcRequest(payload)) {
           this.core.history.set(topic, payload);
-          this.onRelayEventRequest({ topic, payload });
+          await this.onRelayEventRequest({ topic, payload });
         } else if (isJsonRpcResponse(payload)) {
           await this.core.history.resolve(payload);
           await this.onRelayEventResponse({ topic, payload });
           this.core.history.delete(topic, payload.id);
         }
+        await this.core.relayer.messages.ack(topic, message);
       } catch (error) {
         this.logger.error(error);
       }
     });
   }
 
-  private onRelayEventRequest: IPairingPrivate["onRelayEventRequest"] = (event) => {
+  private onRelayEventRequest: IPairingPrivate["onRelayEventRequest"] = async (event) => {
     const { topic, payload } = event;
     const reqMethod = payload.method as PairingJsonRpcTypes.WcMethod;
 
     switch (reqMethod) {
       case "wc_pairingPing":
-        return this.onPairingPingRequest(topic, payload);
+        return await this.onPairingPingRequest(topic, payload);
       case "wc_pairingDelete":
-        return this.onPairingDeleteRequest(topic, payload);
+        return await this.onPairingDeleteRequest(topic, payload);
       default:
-        return this.onUnknownRpcMethodRequest(topic, payload);
+        return await this.onUnknownRpcMethodRequest(topic, payload);
     }
   };
 
```

### packages/core/src/controllers/relayer.ts
```diff
@@ -60,6 +60,7 @@ import {
   SUBSCRIBER_EVENTS,
   RELAYER_RECONNECT_TIMEOUT,
   TRANSPORT_TYPES,
+  MESSAGE_DIRECTION,
 } from "../constants";
 import { MessageTracker } from "./messages";
 import { Publisher } from "./publisher";
@@ -157,13 +158,16 @@ export class Relayer extends IRelayer {
   public async publish(topic: string, message: string, opts?: RelayerTypes.PublishOptions) {
     this.isInitialized();
     await this.publisher.publish(topic, message, opts);
-    await this.recordMessageEvent({
-      topic,
-      message,
-      // We don't have `publishedAt` from the relay server on outgoing, so use current time to satisfy type.
-      publishedAt: Date.now(),
-      transportType: TRANSPORT_TYPES.relay,
-    });
+    await this.recordMessageEvent(
+      {
+        topic,
+        message,
+        // We don't have `publishedAt` from the relay server on outgoing, so use current time to satisfy type.
+        publishedAt: Date.now(),
+        transportType: TRANSPORT_TYPES.relay,
+      },
+      MESSAGE_DIRECTION.outbound,
+    );
   }
 
   public async subscribe(topic: string, opts?: RelayerTypes.SubscribeOptions) {
@@ -343,7 +347,7 @@ export class Relayer extends IRelayer {
     }
 
     this.events.emit(RELAYER_EVENTS.message, messageEvent);
-    await this.recordMessageEvent(messageEvent);
+    await this.recordMessageEvent(messageEvent, MESSAGE_DIRECTION.inbound);
   }
 
   // ---------- Private ----------------------------------------------- //
@@ -484,9 +488,12 @@ export class Relayer extends IRelayer {
     this.registerProviderListeners();
   }
 
-  private async recordMessageEvent(messageEvent: RelayerTypes.MessageEvent) {
+  private async recordMessageEvent(
+    messageEvent: RelayerTypes.MessageEvent,
+    direction?: RelayerTypes.MessageDirection,
+  ) {
     const { topic, message } = messageEvent;
-    await this.messages.set(topic, message);
+    await this.messages.set(topic, message, direction);
   }
 
   private async shouldIgnoreMessageEvent(
@@ -500,9 +507,9 @@ export class Relayer extends IRelayer {
       return true;
     }
 
-    // Ignore if `topic` is not subscribed to.
-    if (!(await this.subscriber.isSubscribed(topic))) {
-      this.logger.warn(`Ignoring message for non-subscribed topic ${topic}`);
+    // Ignore if `topic` is not known to the subscriber.
+    if (!(await this.subscriber.isKnownTopic(topic))) {
+      this.logger.warn(`Ignoring message for unknown topic ${topic}`);
       return true;
     }
 
@@ -542,8 +549,8 @@ export class Relayer extends IRelayer {
     if (await this.shouldIgnoreMessageEvent(messageEvent)) {
       return;
     }
+    await this.recordMessageEvent(messageEvent, MESSAGE_DIRECTION.inbound);
     this.events.emit(RELAYER_EVENTS.message, messageEvent);
-    await this.recordMessageEvent(messageEvent);
   }
 
   private async acknowledgePayload(payload: JsonRpcPayload) {
```

### packages/core/src/controllers/subscriber.ts
```diff
@@ -3,7 +3,7 @@ import { HEARTBEAT_EVENTS } from "@walletconnect/heartbeat";
 import { ErrorResponse, RequestArguments } from "@walletconnect/jsonrpc-types";
 import { generateChildLogger, getLoggerContext, Logger } from "@walletconnect/logger";
 import { RelayJsonRpc } from "@walletconnect/relay-api";
-import { ONE_SECOND, ONE_MINUTE, Watch, toMiliseconds } from "@walletconnect/time";
+import { ONE_SECOND, ONE_MINUTE, toMiliseconds } from "@walletconnect/time";
 import {
   IRelayer,
   ISubscriber,
@@ -25,7 +25,6 @@ import {
   SUBSCRIBER_CONTEXT,
   SUBSCRIBER_EVENTS,
   SUBSCRIBER_STORAGE_VERSION,
-  PENDING_SUB_RESOLUTION_TIMEOUT,
   RELAYER_EVENTS,
   TRANSPORT_TYPES,
 } from "../constants";
@@ -41,8 +40,6 @@ export class Subscriber extends ISubscriber {
 
   private cached: SubscriberTypes.Active[] = [];
   private initialized = false;
-  private pendingSubscriptionWatchLabel = "pending_sub_watch_label";
-  private pollingInterval = 20;
   private storagePrefix = CORE_STORAGE_PREFIX;
   private subscribeTimeout = toMiliseconds(ONE_MINUTE);
   private initialSubscribeTimeout = toMiliseconds(ONE_SECOND * 15);
@@ -131,31 +128,26 @@ export class Subscriber extends ISubscriber {
     }
   };
 
-  public isSubscribed: ISubscriber["isSubscribed"] = async (topic: string) => {
-    // topic subscription is already resolved
-    if (this.topics.includes(topic)) return true;
-    const label = `${this.pendingSubscriptionWatchLabel}_${topic}`;
-    // wait for the subscription to resolve
-    const exists = await new Promise<boolean>((resolve, reject) => {
-      const watch = new Watch();
-      watch.start(label);
-      const interval = setInterval(() => {
-        if (
-          (!this.pending.has(topic) && this.topics.includes(topic)) ||
-          this.cached.some((s) => s.topic === topic)
-        ) {
-          clearInterval(interval);
-          watch.stop(label);
-          resolve(true);
-        }
-        if (watch.elapsed(label) >= PENDING_SUB_RESOLUTION_TIMEOUT) {
-          clearInterval(interval);
-          watch.stop(label);
-          reject(new Error("Subscription resolution timeout"));
-        }
-      }, this.pollingInterval);
-    }).catch(() => false);
-    return exists;
+  /**
+   * returns `true` only if the topic is actively subscribed to i.e. not pending or cached
+   */
+  public isSubscribed: ISubscriber["isSubscribed"] = (topic: string) => {
+    return new Promise((resolve) => {
+      resolve(this.topicMap.topics.includes(topic));
+    });
+  };
+
+  /**
+   * returns `true` if the topic is known to the subscriber i.e. it is actively subscribed, pending, cached or in the topic map
+   */
+  public isKnownTopic: ISubscriber["isKnownTopic"] = (topic: string) => {
+    return new Promise((resolve) => {
+      resolve(
+        this.topicMap.topics.includes(topic) ||
+          this.pending.has(topic) ||
+          this.cached.some((s) => s.topic === topic),
+      );
+    });
   };
 
   public on: ISubscriber["on"] = (event, listener) => {
```

### packages/core/test/messages.spec.ts
```diff
@@ -6,6 +6,7 @@ import {
   Core,
   CORE_DEFAULT,
   CORE_STORAGE_PREFIX,
+  MESSAGE_DIRECTION,
   MESSAGES_CONTEXT,
   MESSAGES_STORAGE_VERSION,
   MessageTracker,
@@ -49,10 +50,12 @@ describe("Messages", () => {
     });
     it("sets an entry on the messages map for a new topic-message pair", async () => {
       const mockMessage = "test message";
-      await messageTracker.set(topic, mockMessage);
+      await messageTracker.set(topic, mockMessage, MESSAGE_DIRECTION.inbound);
       const key = hashMessage(mockMessage);
       const message = messageTracker.messages.get(topic) ?? {};
       expect(message[key]).to.equal(mockMessage);
+      const messagesWithoutClientAck = messageTracker.messagesWithoutClientAck.get(topic) ?? {};
+      expect(messagesWithoutClientAck[key]).to.equal(mockMessage);
     });
   });
 
@@ -67,8 +70,10 @@ describe("Messages", () => {
     });
     it("returns the expected message based on the topic", async () => {
       const mockMessage = "test message";
-      await messageTracker.set(topic, mockMessage);
+      await messageTracker.set(topic, mockMessage, MESSAGE_DIRECTION.inbound);
       expect(messageTracker.get(topic)).to.deep.equal({ [hashMessage(mockMessage)]: mockMessage });
+      const messagesWithoutClientAck = messageTracker.messagesWithoutClientAck.get(topic) ?? {};
+      expect(messagesWithoutClientAck[hashMessage(mockMessage)]).to.equal(mockMessage);
     });
   });
 
@@ -95,10 +100,93 @@ describe("Messages", () => {
       await expect(invalidMessageTracker.del(topic)).rejects.toThrow("Not initialized. messages");
     });
     it("removes the matching topic-message pair for the provided topic", async () => {
-      await messageTracker.set(topic, "message");
+      await messageTracker.set(topic, "message", MESSAGE_DIRECTION.inbound);
       expect(messageTracker.messages.size).to.equal(1);
+      expect(messageTracker.messagesWithoutClientAck.size).to.equal(1);
       await messageTracker.del(topic);
       expect(messageTracker.messages.size).to.equal(0);
+      expect(messageTracker.messagesWithoutClientAck.size).to.equal(0);
+    });
+  });
+
+  describe("ack", () => {
+    it("throws if not initialized", async () => {
+      const invalidMessageTracker = new MessageTracker(logger, new Core(TEST_CORE_OPTIONS));
+      await expect(invalidMessageTracker.ack(topic, "message")).rejects.toThrow(
+        "Not initialized. messages",
+      );
+    });
+    it("removes the the topic-message pair from `messagesWithoutClientAck` when acknowledged", async () => {
+      await messageTracker.set(topic, "message", MESSAGE_DIRECTION.inbound);
+      await messageTracker.ack(topic, "message");
+      expect(messageTracker.messages.size).to.equal(1);
+      expect(messageTracker.messagesWithoutClientAck.size).to.equal(0);
+    });
+
+    it("doesn't store outbound messages in `messagesWithoutClientAck`", async () => {
+      await messageTracker.set(topic, "message", MESSAGE_DIRECTION.outbound);
+      expect(messageTracker.messages.size).to.equal(1);
+      expect(messageTracker.messagesWithoutClientAck.size).to.equal(0);
+    });
+
+    it("doesn't throw if the topic-message pair doesn't exist", async () => {
+      expect(await messageTracker.ack(topic, "message")).to.be.undefined;
+    });
+  });
+
+  describe("getWithoutAck", () => {
+    it("returns an empty map if no topics are provided", () => {
+      expect(messageTracker.getWithoutAck([])).to.deep.equal({});
+    });
+
+    it("returns empty map if no messages are available for the provided topic", () => {
+      expect(messageTracker.getWithoutAck([topic])).to.deep.equal({ [topic]: [] });
+    });
+    it("returns correct messages for the provided topic", async () => {
+      const mockMessage = "test message";
+      await messageTracker.set(topic, mockMessage, MESSAGE_DIRECTION.inbound);
+      expect(messageTracker.getWithoutAck([topic])).to.deep.equal({
+        [topic]: [mockMessage],
+      });
+    });
+    it("returns correct messages for multiple provided topics", async () => {
+      const mockMessage = "test message";
+      const topic2 = generateRandomBytes32();
+      await messageTracker.set(topic, mockMessage, MESSAGE_DIRECTION.inbound);
+      await messageTracker.set(topic2, mockMessage, MESSAGE_DIRECTION.inbound);
+      expect(messageTracker.getWithoutAck([topic, topic2])).to.deep.equal({
+        [topic]: [mockMessage],
+        [topic2]: [mockMessage],
+      });
+    });
+    it("returns correct messages for multiple provided topics. Test 2", async () => {
+      const mockMessage = "test message";
+      const mockMessage2 = "test message 2";
+      const mockMessage3 = "test message 3";
+      const topic2 = generateRandomBytes32();
+      const topic3 = generateRandomBytes32();
+      await messageTracker.set(topic, mockMessage, MESSAGE_DIRECTION.inbound);
+      await messageTracker.set(topic2, mockMessage2, MESSAGE_DIRECTION.inbound);
+      await messageTracker.set(topic3, mockMessage3, MESSAGE_DIRECTION.inbound);
+      expect(messageTracker.getWithoutAck([topic2, topic3])).to.deep.equal({
+        [topic2]: [mockMessage2],
+        [topic3]: [mockMessage3],
+      });
+    });
+    it("returns correct messages for multiple provided topics. Test 3", async () => {
+      const mockMessage = "test message";
+      const mockMessage2 = "test message 2";
+      const mockMessage3 = "test message 3";
+      const topic2 = generateRandomBytes32();
+      const topic3 = generateRandomBytes32();
+      await messageTracker.set(topic, mockMessage, MESSAGE_DIRECTION.inbound);
+      await messageTracker.set(topic, mockMessage2, MESSAGE_DIRECTION.inbound);
+      await messageTracker.set(topic2, mockMessage3, MESSAGE_DIRECTION.inbound);
+      expect(messageTracker.getWithoutAck([topic, topic2, topic3])).to.deep.equal({
+        [topic]: [mockMessage, mockMessage2],
+        [topic2]: [mockMessage3],
+        [topic3]: [],
+      });
     });
   });
 });
```

### packages/sign-client/src/controllers/engine.ts
```diff
@@ -171,13 +171,39 @@ export class Engine extends IEngine {
       await this.registerLinkModeListeners();
       this.client.core.pairing.register({ methods: Object.keys(ENGINE_RPC_OPTS) });
       this.initialized = true;
-      setTimeout(() => {
+      setTimeout(async () => {
+        await this.processPendingMessageEvents();
+
         this.sessionRequestQueue.queue = this.getPendingSessionRequests();
         this.processSessionRequestQueue();
       }, toMiliseconds(this.requestQueueDelay));
     }
   };
 
+  private async processPendingMessageEvents() {
+    try {
+      const topics = this.client.session.keys;
+      const pendingMessages = this.client.core.relayer.messages.getWithoutAck(topics);
+      for (const [topic, messages] of Object.entries(pendingMessages)) {
+        for (const message of messages) {
+          try {
+            await this.onProviderMessageEvent({
+              topic,
+              message,
+              publishedAt: Date.now(),
+            });
+          } catch (error) {
+            this.client.logger.warn(
+              `Error processing pending message event for topic: ${topic}, message: ${message}`,
+            );
+          }
+        }
+      }
+    } catch (error) {
+      this.client.logger.warn("processPendingMessageEvents failed", error);
+    }
+  }
+
   // ---------- Public ------------------------------------------------ //
 
   public connect: IEngine["connect"] = async (params) => {
@@ -1657,15 +1683,19 @@ export class Engine extends IEngine {
 
   private registerRelayerEvents() {
     this.client.core.relayer.on(RELAYER_EVENTS.message, (event: RelayerTypes.MessageEvent) => {
-      // capture any messages that arrive before the client is initialized so we can process them after initialization is complete
-      if (!this.initialized || this.relayMessageCache.length > 0) {
-        this.relayMessageCache.push(event);
-      } else {
-        this.onRelayMessage(event);
-      }
+      this.onProviderMessageEvent(event);
     });
   }
 
+  private onProviderMessageEvent = async (event: RelayerTypes.MessageEvent) => {
+    // capture any messages that arrive before the client is initialized so we can process them after initialization is complete
+    if (!this.initialized || this.relayMessageCache.length > 0) {
+      this.relayMessageCache.push(event);
+    } else {
+      await this.onRelayMessage(event);
+    }
+  };
+
   private async onRelayMessage(event: RelayerTypes.MessageEvent) {
     const { topic, message, attestation, transportType } = event;
 
@@ -1674,14 +1704,15 @@ export class Engine extends IEngine {
       ? this.client.auth.authKeys.get(AUTH_PUBLIC_KEY_NAME)
       : ({ responseTopic: undefined, publicKey: undefined } as any);
 
-    const payload = await this.client.core.crypto.decode(topic, message, {
-      receiverPublicKey: publicKey,
-      encoding: transportType === TRANSPORT_TYPES.link_mode ? BASE64URL : BASE64,
-    });
     try {
+      const payload = await this.client.core.crypto.decode(topic, message, {
+        receiverPublicKey: publicKey,
+        encoding: transportType === TRANSPORT_TYPES.link_mode ? BASE64URL : BASE64,
+      });
+
       if (isJsonRpcRequest(payload)) {
         this.client.core.history.set(topic, payload);
-        this.onRelayEventRequest({
+        await this.onRelayEventRequest({
           topic,
           payload,
           attestation,
@@ -1693,8 +1724,9 @@ export class Engine extends IEngine {
         await this.onRelayEventResponse({ topic, payload, transportType });
         this.client.core.history.delete(topic, payload.id);
       } else {
-        this.onRelayEventUnknownPayload({ topic, payload, transportType });
+        await this.onRelayEventUnknownPayload({ topic, payload, transportType });
       }
+      await this.client.core.relayer.messages.ack(topic, message);
     } catch (error) {
       this.client.logger.error(error);
     }
@@ -2141,13 +2173,15 @@ export class Engine extends IEngine {
   private onSessionPingResponse: EnginePrivate["onSessionPingResponse"] = (_topic, payload) => {
     const { id } = payload;
     const target = engineEvent("session_ping", id);
-    const listeners = this.events.listenerCount(target);
-    if (listeners === 0) {
-      throw new Error(`emitting ${target} without any listeners`);
-    }
+
     // put at the end of the stack to avoid a race condition
     // where session_ping listener is not yet initialized
     setTimeout(() => {
+      const listeners = this.events.listenerCount(target);
+      if (listeners === 0) {
+        throw new Error(`emitting ${target} without any listeners 2176`);
+      }
+
       if (isJsonRpcResult(payload)) {
         this.events.emit(engineEvent("session_ping", id), {});
       } else if (isJsonRpcError(payload)) {
```

### packages/sign-client/test/sdk/persistence.spec.ts
```diff
@@ -11,7 +11,11 @@ import {
   TEST_SIGN_CLIENT_OPTIONS_B,
   TEST_SIGN_CLIENT_OPTIONS_A,
   TEST_NAMESPACES,
+  TEST_APP_METADATA_A,
+  TEST_SIGN_CLIENT_NAME_A,
 } from "../shared";
+import { Core, RELAYER_EVENTS } from "@walletconnect/core";
+import { RelayerTypes } from "@walletconnect/types";
 
 const generateClientDbName = (prefix: string) =>
   `./test/tmp/${prefix}_${generateRandomBytes32()}.db`;
@@ -386,5 +390,71 @@ describe("Sign Client Persistence", () => {
 
       await deleteClients(clients);
     });
+    /**
+     * this test simulates a case where `Core` receives a message mid initialization
+     * before the implementing client (sign-client) is ready to process it
+     * the message should be queued and processed after the client is ready
+     */
+    it("should process pending messages after restart", async () => {
+      const db_a = generateClientDbName("client_a");
+      const clients = await initTwoClients(
+        {
+          storageOptions: { database: db_a },
+        },
+        {},
+      );
+      const {
+        sessionA: { topic },
+      } = await testConnectMethod(clients);
+      let messageEvent: RelayerTypes.MessageEvent;
+      await Promise.all([
+        new Promise<void>((resolve) => {
+          clients.A.core.relayer.once(
+            RELAYER_EVENTS.message,
+            (event: RelayerTypes.MessageEvent) => {
+              messageEvent = event;
+              resolve();
+            },
+          );
+        }),
+        clients.B.ping({ topic }),
+      ]);
+      await clients.A.core.relayer.transportClose();
+      await throttle(1000);
+      const core = new Core({
+        storageOptions: { database: db_a },
+        projectId: process.env.TEST_PROJECT_ID,
+      });
+      let onMessageEventTimestamp: number;
+      core.relayer.on(RELAYER_EVENTS.connect, async () => {
+        // delete the message from the relayer so it can be processed again
+        await core.relayer.messages.del(topic);
+        // @ts-expect-error - private method
+        await core.relayer.onMessageEvent(messageEvent);
+        onMessageEventTimestamp = Date.now();
+        if (core.relayer.messages.messagesWithoutClientAck.size !== 1) {
+          throw new Error("message not queued for processing");
+        }
+      });
+
+      const wallet = await SignClient.init({
+        name: TEST_SIGN_CLIENT_NAME_A,
+        metadata: TEST_APP_METADATA_A,
+        core,
+      });
+      const walletInitTimestamp = Date.now();
+
+      // validate that the message was received before the wallet was initialized
+      expect(walletInitTimestamp).toBeGreaterThan(onMessageEventTimestamp);
+      // validate that the message was processed by the wallet even though it was received before the wallet was initialized
+      await new Promise<void>((resolve) => {
+        wallet.on("session_ping", () => {
+          resolve();
+        });
+      });
+      await throttle(1000);
+      expect(core.relayer.messages.messagesWithoutClientAck.size).toBe(0);
+      await deleteClients({ A: wallet, B: clients.B });
+    });
   });
 });
```

### packages/types/src/core/messages.ts
```diff
@@ -5,6 +5,7 @@ export type MessageRecord = Record<string, string>;
 
 export abstract class IMessageTracker {
   public abstract messages: Map<string, MessageRecord>;
+  public abstract messagesWithoutClientAck: Map<string, MessageRecord>;
 
   public abstract name: string;
 
@@ -14,11 +15,19 @@ export abstract class IMessageTracker {
 
   public abstract init(): Promise<void>;
 
-  public abstract set(topic: string, message: string): Promise<string>;
+  public abstract set(
+    topic: string,
+    message: string,
+    direction?: "inbound" | "outbound",
+  ): Promise<string>;
 
   public abstract get(topic: string): MessageRecord;
 
+  public abstract getWithoutAck(topics: string[]): Record<string, string[]>;
+
   public abstract has(topic: string, message: string): boolean;
 
   public abstract del(topic: string): Promise<void>;
+
+  public abstract ack(topic: string, message: string): Promise<void>;
 }
```

### packages/types/src/core/pairing.ts
```diff
@@ -120,7 +120,7 @@ export interface IPairingPrivate {
 
   sendError(id: number, topic: string, error: PairingJsonRpcTypes.Error): Promise<void>;
 
-  onRelayEventRequest(event: PairingJsonRpcTypes.EventCallback<JsonRpcRequest>): void;
+  onRelayEventRequest(event: PairingJsonRpcTypes.EventCallback<JsonRpcRequest>): Promise<void>;
 
   onRelayEventResponse(event: PairingJsonRpcTypes.EventCallback<JsonRpcResponse>): Promise<void>;
 
```

### packages/types/src/core/relayer.ts
```diff
@@ -74,6 +74,8 @@ export declare namespace RelayerTypes {
     txHashes?: string[];
     contractAddresses?: string[];
   }
+
+  export type MessageDirection = "inbound" | "outbound";
 }
 
 export interface RelayerOptions {
```

### packages/types/src/core/subscriber.ts
```diff
@@ -76,6 +76,8 @@ export abstract class ISubscriber extends IEvents {
 
   public abstract isSubscribed(topic: string): Promise<boolean>;
 
+  public abstract isKnownTopic(topic: string): Promise<boolean>;
+
   public abstract start(): Promise<void>;
 
   public abstract stop(): Promise<void>;
```
