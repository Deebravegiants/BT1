# [?] fix(apps-backend): crashed apps-backend (#3555)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-10-24
Source: https://github.com/iotaledger/iota/commit/4647c11f4d337842628ee9015593dea27ff7d145
Type: security-commit

## Details
fix(apps-backend): crashed apps-backend (#3555)

* fix(apps-backend): remove from package & use compiled part of iota/core.

* fix(apps-backend): revert remove iota/core.

* fix(apps-backend): change vercel config

---------

Co-authored-by: Marc Espin <mespinsanz@gmail.com>

## Patch
### .github/workflows/apps-backend-preview.deploy.yml
```diff
@@ -0,0 +1,62 @@
+name: Preview Deploy for Apps Backend
+
+env:
+  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
+  VERCEL_PROJECT_ID: ${{ secrets.APPS_BACKEND_VERCEL_PROJECT_ID }}
+
+on:
+  pull_request:
+    paths:
+      - "apps/apps-backend/**"
+      - ".github/workflows/apps-backend-preview.deploy.yml"
+
+jobs:
+  deploy-preview:
+    permissions:
+      contents: read
+      pull-requests: write
+    runs-on: [self-hosted]
+    steps:
+      - uses: actions/checkout@eef61447b9ff4aafe5dcd4e0bbf5d482be7e7871 # pin@v4
+      - uses: pnpm/action-setup@fe02b34f77f8bc703788d5817da081398fad5dd2 # pin@v4
+      - name: Install Nodejs
+        uses: actions/setup-node@0a44ba7841725637a19e28fa30b79a866c81b0a6 # pin@v4
+        with:
+          node-version: "20"
+          cache: "pnpm"
+      - name: Install dependencies
+        run: pnpm install --frozen-lockfile
+      - name: Turbo Cache
+        id: turbo-cache
+        uses: actions/cache@3624ceb22c1c5a301c8db4169662070a689d9ea8 # pin@v4
+        with:
+          path: node_modules/.cache/turbo
+          key: turbo-${{ runner.os }}-${{ github.sha }}
+          restore-keys: |
+            turbo-${{ runner.os }}-
+      - name: Install Vercel CLI
+        run: pnpm add --global vercel@canary
+      - name: Build the Apps Backend
+        run: pnpm apps-backend build
+      - name: Pull Vercel Environment
+        run: vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}
+      - name: Build Project Artifacts
+        run: vercel build --token=${{ secrets.VERCEL_TOKEN }}
+      - name: Deploy Project Artifacts to Vercel
+        run: vercel deploy --prebuilt --token=${{ secrets.VERCEL_TOKEN }} > vercel_output.txt
+      - name: Extract Deploy URL
+        id: deploy_url
+        run: echo "DEPLOY_URL=$(cat vercel_output.txt | awk 'END{print}')" >> $GITHUB_OUTPUT
+      - name: Comment on pull request
+        uses: actions/github-script@60a0d83039c74a4aee543508d2ffcb1c3799cdea # pin@v7
+        with:
+          github-token: ${{ secrets.GITHUB_TOKEN }}
+          script: |
+            const DEPLOY_URL = '${{ steps.deploy_url.outputs.DEPLOY_URL }}'
+            const COMMIT_SHA = '${{ github.event.pull_request.head.sha }}'
+            github.rest.issues.createComment({
+              issue_number: context.issue.number,
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+              body: `This pull request has been deployed to Vercel.\n\n\nLatest commit: ${COMMIT_SHA}\n\n:white_check_mark: Preview: ${DEPLOY_URL}`
+            })
```

### apps/apps-backend/nest-cli.json
```diff
@@ -4,5 +4,6 @@
     "sourceRoot": "src",
     "compilerOptions": {
         "deleteOutDir": true
-    }
+    },
+    "entryFile": "apps-backend/src/main.js"
 }
```

### apps/apps-backend/tsconfig.json
```diff
@@ -18,7 +18,7 @@
         "forceConsistentCasingInFileNames": false,
         "noFallthroughCasesInSwitch": false,
         "paths": {
-            "@iota/core/constants/*": ["./node_modules/@iota/core/dist/constants/*"]
+            "@iota/core/constants/*": ["./../core/src/constants/*"]
         }
     },
 }
```

### apps/apps-backend/vercel.json
```diff
@@ -2,15 +2,14 @@
     "version": 2,
     "builds": [
         {
-            "src": "src/main.ts",
+            "src": "dist/apps-backend/src/main.js",
             "use": "@vercel/node"
         }
     ],
     "routes": [
         {
             "src": "/(.*)",
-            "dest": "src/main.ts",
-            "methods": ["GET", "POST", "PUT", "DELETE"]
+            "dest": "dist/apps-backend/src/main.js"
         }
     ]
 }
```
