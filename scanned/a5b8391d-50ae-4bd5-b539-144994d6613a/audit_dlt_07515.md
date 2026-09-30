# [?] Prevent node crashing when logger fails to serialize BigInt by using string interpolation (#672)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2022-01-04
Source: https://github.com/iron-fish/ironfish/commit/8be873eeb1414aa977d105530c49327f95ae9cb9
Type: security-commit

## Details
Prevent node crashing when logger fails to serialize BigInt by using string interpolation (#672)

* Prevent node crashing when logger fails to serialize BigInt by using string interpolation

* Serializing logObj.arg on the InterceptReporter level

* changing test

* Get rid of quotes and bracets in logs and getting them prettier

* Revert "Get rid of quotes and bracets in logs and getting them prettier"

This reverts commit af1281380452db23ec2dee2beaf295240f80129a.

* Preventing node crashing because of poor serializing

* Getting rid of quotes and square brackets in the logs and prettifing logs a bit

* Get rid of quotes and bracets in logs and getting them prettier

* Revert "Get rid of quotes and bracets in logs and getting them prettier"

This reverts commit af1281380452db23ec2dee2beaf295240f80129a.

* Preventing node crashing because of poor serializing

* Getting rid of quotes and square brackets in the logs and prettifing logs a bit

* Fixed getLogStream test

* Get rid of quotes and bracets in logs and getting them prettier

* Revert "Get rid of quotes and bracets in logs and getting them prettier"

This reverts commit af1281380452db23ec2dee2beaf295240f80129a.

* Preventing node crashing because of poor serializing

* Getting rid of quotes and square brackets in the logs and prettifing logs a bit

* Review fixes

* Review fixes

* Change serialization

Co-authored-by: Vladimir Tsybulskiy <vovan@Vladimirs-MacBook-Pro.local>
Co-authored-by: Derek Guenther <dguenther9@gmail.com>

## Patch
### ironfish-cli/src/commands/logs.ts
```diff
@@ -2,7 +2,7 @@
  * License, v. 2.0. If a copy of the MPL was not distributed with this
  * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
 import { logType } from 'consola'
-import { ConsoleReporterInstance, IronfishNode } from 'ironfish'
+import { ConsoleReporterInstance, IJSON, IronfishNode } from 'ironfish'
 import { IronfishCommand } from '../command'
 import { RemoteFlags } from '../flags'
 
@@ -23,11 +23,19 @@ export default class LogsCommand extends IronfishCommand {
     const response = this.sdk.client.getLogStream()
 
     for await (const value of response.contentStream()) {
+      let parsedArgs
+      try {
+        parsedArgs = IJSON.parse(value.args) as unknown[]
+      } catch (e) {
+        this.logger.error(`Failed to deserialize args: ${value.args}`)
+        throw e
+      }
+
       ConsoleReporterInstance.log({
         level: Number(value.level),
         type: value.type as logType,
         tag: value.tag,
-        args: value.args,
+        args: parsedArgs,
         date: new Date(value.date),
       })
     }
```

### ironfish/src/rpc/routes/node/getLogStream.test.ts
```diff
@@ -25,7 +25,30 @@ describe('Route node/getLogStream', () => {
       level: LogLevel.Info.toString(),
       tag: expect.stringContaining('ironfishnode'),
       type: 'info',
-      args: ['Hello', { foo: 2 }],
+      args: '["Hello",{"foo":2}]',
+      date: expect.anything(),
+    })
+  })
+
+  it('should encode bigints', async () => {
+    // Clear out the console reporter
+    routeTest.node.logger.setReporters([])
+    // Start accepting logs again
+    routeTest.node.logger.resume()
+
+    const response = await routeTest.adapter.requestStream('node/getLogStream').waitForRoute()
+
+    routeTest.node.logger.info(BigInt(2))
+    const { value } = await response.contentStream().next()
+
+    response.end()
+    expect(response.status).toBe(200)
+
+    expect(value).toMatchObject({
+      level: LogLevel.Info.toString(),
+      tag: expect.stringContaining('ironfishnode'),
+      type: 'info',
+      args: '["2n"]',
       date: expect.anything(),
     })
   })
```

### ironfish/src/rpc/routes/node/getLogStream.ts
```diff
@@ -4,6 +4,7 @@
 import { ConsolaReporterLogObject } from 'consola'
 import * as yup from 'yup'
 import { InterceptReporter } from '../../../logger'
+import { IJSON } from '../../../serde'
 import { ApiNamespace, router } from '../router'
 
 // eslint-disable-next-line @typescript-eslint/ban-types
@@ -13,7 +14,7 @@ export type GetLogStreamResponse = {
   level: string
   type: string
   tag: string
-  args: unknown[]
+  args: string
   date: string
 }
 
@@ -27,7 +28,7 @@ export const GetLogStreamResponseSchema: yup.ObjectSchema<GetLogStreamResponse>
     level: yup.string().defined(),
     type: yup.string().defined(),
     tag: yup.string().defined(),
-    args: yup.array(yup.mixed()).defined(),
+    args: yup.string().defined(),
     date: yup.string().defined(),
   })
   .defined()
@@ -41,7 +42,7 @@ router.register<typeof GetLogStreamRequestSchema, GetLogStreamResponse>(
         level: String(logObj.level),
         type: logObj.type,
         tag: logObj.tag,
-        args: logObj.args,
+        args: IJSON.stringify(logObj.args),
         date: logObj.date.toISOString(),
       })
     })
```
