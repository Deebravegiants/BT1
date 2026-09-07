# [H] Flowise has Arbitrary File Upload via MIME Spoofing

## Summary
Severity: High
Advisory: GHSA-j8g8-j7fc-43v6
CVE: CVE-2026-30821
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-j8g8-j7fc-43v6
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.13

## Details
### Vulnerability **Description**

---

**Vulnerability Overview**
 
- The `/api/v1/attachments/:chatflowId/:chatId` endpoint is listed in `WHITELIST_URLS`, allowing unauthenticated access to the file upload API.
- While the server validates uploads based on the MIME types defined in `chatbotConfig.fullFileUpload.allowedUploadFileTypes`, it implicitly trusts the client-provided `Content-Type` header (`file.mimetype`) without verifying the file's actual content (magic bytes) or extension (`file.originalname`).
- Consequently, an attacker can bypass this restriction by spoofing the `Content-Type` as a permitted type (e.g., `application/pdf`) while uploading malicious scripts or arbitrary files. Once uploaded via `addArrayFilesToStorage`, these files persist in backend storage (S3, GCS, or local disk). This vulnerability serves as a critical entry point that, when chained with other features like static hosting or file retrieval, can lead to Stored XSS, malicious file hosting, or Remote Code Execution (RCE).

**Vulnerable Code**

- Upload Route Definition
    
    https://github.com/FlowiseAI/Flowise/blob/d17c4394a238b49327b493c89feee45f3a20bb91/packages/server/src/routes/attachments/index.ts#L7-L10
    
    ```tsx
    // CREATE
    router.post('/:chatflowId/:chatId', getMulterStorage().array('files'), attachmentsController.createAttachment)
    export default router
    ```
    
- Mount /api/v1/attachments to the global router
    
    https://github.com/FlowiseAI/Flowise/blob/d17c4394a238b49327b493c89feee45f3a20bb91/packages/server/src/routes/index.ts#L72-L77
    
    ```tsx
    const router = express.Router()
    router.use('/ping', pingRouter)
    router.use('/apikey', apikeyRouter)
    router.use('/assistants', assistantsRouter)
    router.use('/attachments', attachmentsRouter)
    ```
    
- Include /api/v1/attachments in the WHITELIST_URLS list
    
    https://github.com/FlowiseAI/Flowise/blob/d17c4394a238b49327b493c89feee45f3a20bb91/packages/server/src/utils/constants.ts#L6-L26
    
    ```tsx
    export const WHITELIST_URLS = [
        '/api/v1/verify/apikey/',
        '/api/v1/chatflows/apikey/',
        '/api/v1/public-chatflows',
        '/api/v1/public-chatbotConfig',
        '/api/v1/public-executions',
        '/api/v1/prediction/',
        '/api/v1/vector/upsert/',
        '/api/v1/node-icon/',
        '/api/v1/components-credentials-icon/',
        '/api/v1/chatflows-streaming',
        '/api/v1/chatflows-uploads',
        '/api/v1/openai-assistants-file/download',
        '/api/v1/feedback',
        '/api/v1/leads',
        '/api/v1/get-upload-file',
        '/api/v1/ip',
        '/api/v1/ping',
        '/api/v1/version',
        '/api/v1/attachments',
        '/api/v1/metrics',
    ```
    
- Bypass JWT validation if the URL is whitelisted
    
    https://github.com/FlowiseAI/Flowise/blob/d17c4394a238b49327b493c89feee45f3a20bb91/packages/server/src/index.ts#L213-L228
    
    ```tsx
            const denylistURLs = process.env.DENYLIST_URLS ? process.env.DENYLIST_URLS.split(',') : []
            const whitelistURLs = WHITELIST_URLS.filter((url) => !denylistURLs.includes(url))
            const URL_CASE_INSENSITIVE_REGEX: RegExp = /\/api\/v1\//i
            const URL_CASE_SENSITIVE_REGEX: RegExp = /\/api\/v1\//
    
            await initializeJwtCookieMiddleware(this.app, this.identityManager)
    
            this.app.use(async (req, res, next) => {
                // Step 1: Check if the req path contains /api/v1 regardless of case
                if (URL_CASE_INSENSITIVE_REGEX.test(req.path)) {
                    // Step 2: Check if the req path is casesensitive
                    if (URL_CASE_SENSITIVE_REGEX.test(req.path)) {
                        // Step 3: Check if the req path is in the whitelist
                        const isWhitelisted = whitelistURLs.some((url) => req.path.startsWith(url))
                        if (isWhitelisted) {
                            next()
    ```
    
- Multer Configuration: Saves files without file type validation
    
    https://github.com/FlowiseAI/Flowise/blob/d17c4394a238b49327b493c89feee45f3a20bb91/packages/server/src/utils/index.ts#L1917-L1960
    
    ```tsx
    export const getUploadPath = (): string => {
        return process.env.BLOB_STORAGE_PATH
            ? path.join(process.env.BLOB_STORAGE_PATH, 'uploads')
            : path.join(getUserHome(), '.flowise', 'uploads')
    }
    
    export function generateId() {
        return uuidv4()
    }
    
    export const getMulterStorage = () => {
        const storageType = process.env.STORAGE_TYPE ? process.env.STORAGE_TYPE : 'local'
    
        if (storageType === 's3') {
            const s3Client = getS3Config().s3Client
            const Bucket = getS3Config().Bucket
    
            const upload = multer({
                storage: multerS3({
                    s3: s3Client,
                    bucket: Bucket,
                    metadata: function (req, file, cb) {
                        cb(null, { fieldName: file.fieldname, originalName: file.originalname })
                    },
                    key: function (req, file, cb) {
                        cb(null, `${generateId()}`)
                    }
                })
            })
            return upload
        } else if (storageType === 'gcs') {
            return multer({
                storage: new MulterGoogleCloudStorage({
                    projectId: process.env.GOOGLE_CLOUD_STORAGE_PROJ_ID,
                    bucket: process.env.GOOGLE_CLOUD_STORAGE_BUCKET_NAME,
                    keyFilename: process.env.GOOGLE_CLOUD_STORAGE_CREDENTIAL,
                    uniformBucketLevelAccess: Boolean(process.env.GOOGLE_CLOUD_UNIFORM_BUCKET_ACCESS) ?? true,
                    destination: `uploads/${generateId()}`
                })
            })
        } else {
            return multer({ dest: getUploadPath() })
        }
    }
    ```
    
- Transfers uploaded files to storage without verification
    
    https://github.com/FlowiseAI/Flowise/blob/d17c4394a238b49327b493c89feee45f3a20bb91/packages/server/src/utils/createAttachment.ts#L124-L158
    
    ```tsx
        const files = (req.files as Express.Multer.File[]) || []
        const fileAttachments = []
        if (files.length) {
            const isBase64 = req.body.base64
            for (const file of files) {
                if (!allowedFileTypes.length) {
                    throw new InternalFlowiseError(
                        StatusCodes.BAD_REQUEST,
                        `File type '${file.mimetype}' is not allowed. Allowed types: ${allowedFileTypes.join(', ')}`
                    )
                }
    
                // Validate file type against allowed types
                if (allowedFileTypes.length > 0 && !allowedFileTypes.includes(file.mimetype)) {
                    throw new InternalFlowiseError(
                        StatusCodes.BAD_REQUEST,
                        `File type '${file.mimetype}' is not allowed. Allowed types: ${allowedFileTypes.join(', ')}`
                    )
                }
    
                await checkStorage(orgId, subscriptionId, appServer.usageCacheManager)
    
                const fileBuffer = await getFileFromUpload(file.path ?? file.key)
                const fileNames: string[] = []
                // Address file name with special characters: https://github.com/expressjs/multer/issues/1104
                file.originalname = Buffer.from(file.originalname, 'latin1').toString('utf8')
                const { path: storagePath, totalSize } = await addArrayFilesToStorage(
                    file.mimetype,
                    fileBuffer,
                    file.originalname,
                    fileNames,
                    orgId,
                    chatflowid,
                    chatId
                )
    ```
    

### PoC

---

**PoC Description**
 
- Create a local file named `shell.js` containing arbitrary JavaScript code (or a malicious payload).
- Send a `multipart/form-data` request to the `/api/v1/attachments/891f64a2-a26f-4169-b333-905dc96c200a/:chatId` endpoint without any authentication (login, session, or API keys).
- During the upload, retain the filename as `shell.js` but spoof the `Content-Type` header as `application/pdf`.
- This exploits the server's reliance solely on the client-provided `file.mimetype`, forcing it to process the malicious JS file as an allowed PDF, thereby confirming unauthenticated arbitrary file upload.

**PoC**


```bash
curl -X POST \
  "http://localhost:3000/api/v1/attachments/891f64a2-a26f-4169-b333-905dc96c200a/$(uuidgen)" \
  -F "files=@shell.js;type=application/pdf"
```

<img width="1916" height="1011" alt="image" src="https://github.com/user-attachments/assets/45679d95-00b9-4bee-9c94-7bd9403554d5" />


### Impact

---

**1. Root Cause**
The vulnerability stems from relying solely on the MIME type without cross-validating the file extension or actual content. This allows attackers to upload executable files (e.g., `.js`, `.php`) or malicious scripts (`.html`) by masquerading them as benign images or documents.

**2. Key Attack Scenarios**

- **Server Compromise (RCE):** An attacker uploads a **Web Shell** and triggers its execution on the server. Successful exploitation grants system privileges, allowing unauthorized access to internal data and full control over the server.
- **Client-Side Attack (Stored XSS):** An attacker uploads files containing malicious scripts (e.g., HTML, SVG). When a victim views the file, the script executes within their browser, leading to session cookie theft and account takeover.

**3. Impact**
This vulnerability is rated as **High** severity. The risk is particularly critical if the system utilizes shared storage (e.g., S3, GCS) or static hosting features, as the compromise could spread to the entire infrastructure and affect other tenants.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-j8g8-j7fc-43v6
- https://nvd.nist.gov/vuln/detail/CVE-2026-30821
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.13
