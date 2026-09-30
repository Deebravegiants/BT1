# [?] Problem: minor security issue in github workflow (#1072)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/chain-main
Published: 2024-07-31
Source: https://github.com/crypto-org-chain/chain-main/commit/0bcc2691a287c27622acb548f541e1d781369fd4
Type: security-commit

## Details
Problem: minor security issue in github workflow (#1072)

* Problem: minor security issue in github workflow

* fix PR_PUSHED_AT

## Patch
### .github/workflows/build.yml
```diff
@@ -70,12 +70,17 @@ jobs:
         if: github.event_name == 'issue_comment'
         env:
           COMMENT_BODY: ${{ github.event.comment.body }}
+          COMMENT_DATE: ${{ github.event.comment.created_at }}
         run: |
-          echo "repo_name=${{ fromJson(steps.request.outputs.data).head.repo.full_name }}" >> $GITHUB_OUTPUT
+          PR_PUSHED_AT="${{ fromJson(steps.request.outputs.data).pushed_at }}"
           comment_hash=`echo "$COMMENT_BODY" | cut -d' ' -f2` # get commit hash if any
           if [[ "${comment_hash}" == "/runsim" ]]; then 
-            # use default head ref
-            echo "ref=${{ fromJson(steps.request.outputs.data).head.ref }}" >> $GITHUB_OUTPUT
+            # use default head ref, if the PR hasn't changed since the comment
+            if [[ $(date -d "$PR_PUSHED_AT" +%s) -gt $(date -d "$COMMENT_AT" +%s) ]]; then
+              echo "The PR has changed since the comment, and is therefore not safe to use. Exiting."
+              exit 1
+            fi
+            echo "ref=${{ fromJson(steps.request.outputs.data).head.sha }}" >> $GITHUB_OUTPUT
           else
             # use comment provided ref
             echo "ref=${comment_hash}" >> $GITHUB_OUTPUT
@@ -90,7 +95,6 @@ jobs:
         with:
           submodules: true
           token: ${{ secrets.GITHUB_TOKEN }}
-          repository: ${{ steps.pr_data.outputs.repo_name }}
           ref: ${{ steps.pr_data.outputs.ref }}
       - name: Normal check out code
         uses: actions/checkout@v3
@@ -210,7 +214,6 @@ jobs:
         with:
           submodules: true
           token: ${{ secrets.GITHUB_TOKEN }}
-          repository: ${{ needs.build.outputs.repo_name }}
           ref: ${{ needs.build.outputs.ref }}
       - name: Normal check out code
         uses: actions/checkout@v3
@@ -257,7 +260,6 @@ jobs:
         with:
           submodules: true
           token: ${{ secrets.GITHUB_TOKEN }}
-          repository: ${{ needs.build.outputs.repo_name }}
           ref: ${{ needs.build.outputs.ref }}
       - name: Normal check out code
         uses: actions/checkout@v3
@@ -304,7 +306,6 @@ jobs:
         with:
           submodules: true
           token: ${{ secrets.GITHUB_TOKEN }}
-          repository: ${{ needs.build.outputs.repo_name }}
           ref: ${{ needs.build.outputs.ref }}
       - name: Normal check out code
         uses: actions/checkout@v3
```
