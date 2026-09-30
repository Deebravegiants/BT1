# [?] fix: other assets overflow (#2867)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-09-26
Source: https://github.com/iotaledger/iota/commit/4164c98854d29a39d5daefa77ff767b8ecd10533
Type: security-commit

## Details
fix: other assets overflow (#2867)

Co-authored-by: cpl121 <100352899+cpl121@users.noreply.github.com>

## Patch
### apps/wallet/src/ui/app/pages/home/nfts/NonVisualAssets.tsx
```diff
@@ -30,6 +30,7 @@ export default function NonVisualAssets({ items }: NonVisualAssetsProps) {
                                     <CardBody
                                         title={formatAddress(item.objectId!)}
                                         subtitle={`${formatAddress(address)}::${module}::${name}`}
+                                        isTextTruncated
                                     />
                                     <CardAction
                                         type={CardActionType.Link}
```
