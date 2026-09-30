# [?] fix(migrator): prevent crash by throwing `AggregateError` instead of mutating existing error (#39582)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-01-31
Source: https://github.com/MetaMask/metamask-extension/commit/3e97e0c41554e886d3082da76e78ff4df270aff7
Type: security-commit

## Details
fix(migrator): prevent crash by throwing `AggregateError` instead of mutating existing error (#39582)

## **Description**

We switched migrator error reporting to use AggregateError instead of
rewriting the original error message.

Problem:
Existing migrator tests still expected the old error rewrite behavior,
and didn’t cover v2 migration flow or clone failures.

Solution:
Update migrator unit tests to assert AggregateError emission, verify v2
migration behavior and changed controller reporting, and add a
regression test for clone failures (issue 39567).

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/39582?quickstart=1)

## **Changelog**

<!--
If this PR is not End-User-Facing and should not show up in the
CHANGELOG, you can choose to either:
1. Write `CHANGELOG entry: null`
2. Label with `no-changelog`

If this PR is End-User-Facing, please write a short User-Facing
description in the past tense like:
`CHANGELOG entry: Added a new tab for users to see their NFTs`
`CHANGELOG entry: Fixed a bug that was causing some NFTs to flicker`

(This helps the Release Engineer do their job more quickly and
accurately)
-->

CHANGELOG entry: null

## **Related issues**

Partially Addresses:
https://github.com/MetaMask/metamask-extension/issues/39567
<!--
## **Manual testing steps**

1. Go to this page...
2.
3.

## **Screenshots/Recordings**


### **Before**


### **After**

-->
## **Pre-merge author checklist**

- [ ] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [ ] I've completed the PR template to the best of my ability
- [ ] I’ve included tests if applicable
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [ ] I’ve applied the right labels on the PR (see [labeling
guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [ ] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [ ] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Medium Risk**
> Moderate risk because it changes the shape/type of errors emitted from
the migrator, which may affect any callers/listeners that inspect error
messages or instances. Core migration flow remains the same and is
covered by expanded unit tests, reducing regression risk.
> 
> **Overview**
> **Migrator error reporting now wraps failures in `AggregateError`**
(instead of mutating the original error message) and emits that wrapped
error via the `error` event.
> 
> **Tests were updated and expanded** to assert the new emitted error
shape, verify v2 migration behavior (including `changedKeys` tracking),
and add a regression case for `structuredClone`/`DataCloneError`
failures.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
77d5acd515d1fcd8529c85f5c1b0eeca89c9517e. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

## Patch
### app/scripts/lib/migrator/index.js
```diff
@@ -97,11 +97,13 @@ export default class Migrator extends EventEmitter {
 
         log.info(`Migration ${migration.version} complete`);
       } catch (err) {
-        // rewrite error message to add context without clobbering stack
-        const originalErrorMessage = err.message;
-        err.message = `MetaMask Migration Error #${migration.version}: ${originalErrorMessage}`;
+        // use an AggregateError to add context without clobbering stack
+        const aggregateError = new AggregateError(
+          [err],
+          `MetaMask Migration Error #${migration.version}`,
+        );
         // emit error instead of throw so as to not break the run (gracefully fail)
-        this.emit('error', err);
+        this.emit('error', aggregateError);
         // stop migrating and use state as is
         break;
       }
```

### app/scripts/lib/migrator/index.test.js
```diff
@@ -114,9 +114,84 @@ describe('migrations', () => {
           },
         ],
       });
-      await expect(async () => {
-        await migrator.migrateData({ meta: { version: 0 } });
-      }).rejects.toThrow('Error: MetaMask Migration Error #1: test');
+      const onError = jest.fn();
+      migrator.on('error', onError);
+
+      const initialState = { meta: { version: 0 }, data: { hello: 'world' } };
+      const migratedData = await migrator.migrateData(initialState);
+
+      expect(onError).toHaveBeenCalledTimes(1);
+      const [error] = onError.mock.calls[0];
+      expect(error).toBeInstanceOf(AggregateError);
+      expect(error.message).toBe('MetaMask Migration Error #1');
+      expect(error.errors[0].message).toBe('test');
+      expect(migratedData.state).toBe(initialState);
+    });
+
+    it('runs v2 migrations and reports changed controllers', async () => {
+      const migrate = jest.fn(async (state, localChangedControllers) => {
+        state.meta.version = 187;
+        state.data.foo = 'bar';
+        localChangedControllers.add('TestController');
+      });
+
+      const migrator = new Migrator({
+        migrations: [
+          {
+            version: 187,
+            migrate,
+          },
+        ],
+      });
+
+      const initialState = { meta: { version: 186 }, data: { hello: 'world' } };
+      const migratedData = await migrator.migrateData(initialState);
+
+      expect(migrate).toHaveBeenCalledTimes(1);
+      expect(migrate.mock.calls[0]).toHaveLength(2);
+      expect(migratedData.state).not.toBe(initialState);
+      // toStrictEqual won't work
+      // eslint-disable-next-line jest/prefer-strict-equal
+      expect(migratedData.state.data).toEqual({
+        hello: 'world',
+        foo: 'bar',
+      });
+      expect(migratedData.changedKeys.has('TestController')).toBe(true);
+    });
+
+    it('handles errors thrown when state is cloned for next migration', async () => {
+      const migrate = jest.fn();
+      const migrator = new Migrator({
+        migrations: [
+          {
+            version: 186,
+            migrate,
+          },
+        ],
+      });
+      const onError = jest.fn();
+      migrator.on('error', onError);
+
+      const initialState = {
+        meta: { version: 0 },
+        // Regression test for https://github.com/MetaMask/metamask-extension/issues/39567
+        // `bad` is a function, and cannot be serialized by `structuredClone`
+        // this will throw a DOMException, which doesn't allow its `message`
+        // property to be mutated
+        // eslint-disable-next-line no-empty-function
+        data: { bad: () => {} },
+      };
+      const migratedData = await migrator.migrateData(initialState);
+
+      expect(migrate).not.toHaveBeenCalled();
+      expect(onError).toHaveBeenCalledTimes(1);
+      const [error] = onError.mock.calls[0];
+      expect(error).toBeInstanceOf(AggregateError);
+      expect(error.message).toBe('MetaMask Migration Error #186');
+      expect(error.errors[0]?.constructor?.name).toBe('DOMException');
+      expect(error.errors[0].name).toBe('DataCloneError');
+      expect(error.errors[0].message).toMatch(/could not be cloned/iu);
+      expect(migratedData.state).toBe(initialState);
     });
   });
 });
```
